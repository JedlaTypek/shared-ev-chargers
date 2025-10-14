const { RPCServer, createRPCError } = require('ocpp-rpc');

// Uchovává poslední autorizaci (RFID + čas)
const lastAuthorization = {};
// Sleduje, jestli nabíjení běží
const chargingState = {};
// Pending start – čeká na autorizaci nebo StartTransaction
const pendingStart = {};
// Aktivní transakce – identity nabíječek -> informace o transakci
const activeTransactions = {};

// TTL autorizace – v milisekundách
const AUTH_TTL_MS = 30 * 1000; // 30 sekund

async function start() {
    const server = new RPCServer({
        protocols: ['ocpp1.6'],
        strictMode: true,
    });

    // Jednoduchá autentizace websocketu
    server.auth((accept) => {
        accept({ sessionId: 'XYZ123' });
    });

    server.on('client', async (client) => {
        console.log(`🔌 ${client.identity} connected!`);

        // BootNotification
        client.handle('BootNotification', ({ params }) => {
            console.log(`BootNotification from ${client.identity}:`, params);
            return {
                status: "Accepted",
                interval: 300,
                currentTime: new Date().toISOString()
            };
        });

        // Heartbeat
        client.handle('Heartbeat', () => ({
            currentTime: new Date().toISOString()
        }));

        // Autorizace RFID
        client.handle('Authorize', async ({ params }) => {
            const idTag = params.idTag;
            const now = Date.now();
            const expiryDate = new Date(now + AUTH_TTL_MS).toISOString();
            const isAccepted = idTag === '8B6EDE6E'; // sem dej svou platnou kartu

            lastAuthorization[client.identity] = {
                idTag,
                timestamp: now,
                status: isAccepted ? 'Accepted' : 'Invalid'
            };

            console.log(`Authorize from ${client.identity}: ${idTag} -> ${isAccepted ? 'Accepted' : 'Invalid'} (platí do ${expiryDate})`);

            // Spustit nabíjení, pokud čeká pending start
            const pending = pendingStart[client.identity];
            if (isAccepted && pending) {
                try {
                    await client.call('RemoteStartTransaction', {
                        connectorId: pending.connectorId,
                        idTag
                    });
                    chargingState[client.identity] = { active: true };
                    console.log(`✅ Nabíjení spuštěno po autorizaci (RFID ${idTag})`);
                    delete pendingStart[client.identity];
                } catch (err) {
                    console.error(`⚠️ Chyba při RemoteStartTransaction po autorizaci:`, err);
                }
            }

            return {
                idTagInfo: {
                    status: isAccepted ? 'Accepted' : 'Invalid',
                    expiryDate
                }
            };
        });

        // StatusNotification – start/stop podle statusu
        client.handle('StatusNotification', async ({ params }) => {
            const { status, connectorId = 1 } = params;
            const identity = client.identity;

            console.log(`StatusNotification from ${identity}:`, status);
            chargingState[identity] ??= { active: false };

            if (status === 'Preparing') {
                const auth = lastAuthorization[identity];
                const now = Date.now();

                if (!auth || auth.status !== 'Accepted' || (now - auth.timestamp) > AUTH_TTL_MS) {
                    console.log(`⏳ Preparing bez platné autorizace – čekám`);
                    pendingStart[identity] = { connectorId, timestamp: now };
                    return {};
                }

                if (!chargingState[identity].active) {
                    try {
                        await client.call('RemoteStartTransaction', { connectorId, idTag: auth.idTag });
                        chargingState[identity].active = true;
                        console.log(`✅ Nabíjení spuštěno (RFID ${auth.idTag})`);
                        delete pendingStart[identity];
                    } catch (err) {
                        console.error(`⚠️ Chyba při RemoteStartTransaction:`, err);
                    }
                }
            }

            if (status === 'Finishing' || status === 'Available') {
                const tx = activeTransactions[identity];
                if (tx && tx.transactionId) {
                    try {
                        await client.call('RemoteStopTransaction', { transactionId: tx.transactionId });
                        console.log(`🛑 Nabíjení ukončeno na ${identity}`);
                    } catch (err) {
                        console.error(`⚠️ Chyba při RemoteStopTransaction:`, err);
                    }
                }
                chargingState[identity].active = false;
                delete activeTransactions[identity];
                delete pendingStart[identity];
            }

            return {};
        });

        // StartTransaction – nabíječka hlásí start
        client.handle('StartTransaction', ({ params }) => {
            const { connectorId, idTag, meterStart, timestamp, transactionId } = params;
            const identity = client.identity;

            console.log(`🔌 StartTransaction from ${identity}:`, params);

            activeTransactions[identity] = {
                connectorId,
                idTag,
                meterStart,
                startTime: timestamp,
                transactionId
            };
            chargingState[identity].active = true;

            return {
                transactionId,
                idTagInfo: {
                    status: 'Accepted',
                    expiryDate: new Date(Date.now() + AUTH_TTL_MS).toISOString()
                }
            };
        });

        // StopTransaction – nabíječka hlásí stop
        client.handle('StopTransaction', ({ params }) => {
            const { transactionId, meterStop, timestamp } = params;
            const identity = client.identity;

            const tx = activeTransactions[identity];
            if (tx) {
                console.log(`🛑 StopTransaction from ${identity}:`, {
                    transactionId,
                    meterStop,
                    timestamp,
                    duration: new Date(timestamp) - new Date(tx.startTime),
                    energyUsed: meterStop - tx.meterStart
                });
                chargingState[identity].active = false;
                delete activeTransactions[identity];
            }

            return { idTagInfo: { status: 'Accepted' } };
        });

        // Neznámé RPC metody
        client.handle(({ method, params }) => {
            console.log(`Unhandled method ${method} from ${client.identity}:`, params);
            throw createRPCError("NotImplemented");
        });
    });

    await server.listen(9000, '127.0.0.1');
    console.log("✅ OCPP backend listening on port 9000");
}

start().catch(console.error);
