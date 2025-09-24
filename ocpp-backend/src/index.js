const { RPCServer, createRPCError } = require('ocpp-rpc');

async function start() {
    // vytvoření nového OCPP RPC serveru
    const server = new RPCServer({
        protocols: ['ocpp1.6'], // server akceptuje subprotocol OCPP 1.6
        strictMode: true,       // povolit striktní validaci requestů a responsů
    });

    // autentizace klientů při připojení
    server.auth((accept, reject, handshake) => {
        // přijmout příchozího klienta
        accept({
            // cokoliv tady vrátíš, bude připojeno jako 'session' objekt ke klientovi
            sessionId: 'XYZ123'
        });
    });

    // handler pro nové klienty
    server.on('client', async (client) => {
        console.log(`${client.session.sessionId} connected!`); // `XYZ123 connected!`

        // handler pro BootNotification request
        client.handle('BootNotification', ({ params }) => {
            console.log(`Server got BootNotification from ${client.identity}:`, params);

            // odpověď – přijmout klienta
            return {
                status: "Accepted",
                interval: 300,
                currentTime: new Date().toISOString()
            };
        });

        // handler pro Heartbeat request
        client.handle('Heartbeat', ({ params }) => {
            console.log(`Server got Heartbeat from ${client.identity}:`, params);

            // odpověď – aktuální čas serveru
            return {
                currentTime: new Date().toISOString()
            };
        });

        // handler pro StatusNotification request
        client.handle('StatusNotification', ({ params }) => {
            console.log(`Server got StatusNotification from ${client.identity}:`, params);
            return {}; // prázdná odpověď
        });

        // fallback handler pro neznámé RPC metody
        client.handle(({ method, params }) => {
            console.log(`Server got ${method} from ${client.identity}:`, params);

            // vyhození RPC chyby – metoda není implementovaná
            throw createRPCError("NotImplemented");
        });
    });

    // spuštění serveru na portu 9000
    await server.listen(9000, '127.0.0.1');
    console.log("OCPP backend listening on port 9000");
}

// spustit server
start().catch(console.error);
