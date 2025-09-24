const { RPCServer, createRPCError } = require('ocpp-rpc');
const readline = require('readline');

async function start() {
    const server = new RPCServer({
        protocols: ['ocpp1.6'],
        strictMode: true,
    });

    server.auth((accept) => accept({ sessionId: 'XYZ123' }));

    let currentClient = null;

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function ask(question) {
        return new Promise(resolve => rl.question(question, resolve));
    }

    server.on('client', async (client) => {
        console.log(`${client.session.sessionId} connected!`);
        currentClient = client;

        // Sandbox handler: každý příchozí request čeká na ruční odpověď
        client.handle(async ({ method, params }) => {
            console.log(`Client sent: ${method}`, params);
            const input = await ask(`Odpověď na ${method} (JSON nebo "NotImplemented"): `);

            if (input.trim().toLowerCase() === 'notimplemented') {
                throw createRPCError("NotImplemented");
            }

            try {
                return input ? JSON.parse(input) : {};
            } catch (e) {
                console.log("Chyba v JSON:", e.message);
                throw createRPCError("InternalError", e.message);
            }
        });

        client.on('disconnect', () => {
            console.log(`${client.session.sessionId} disconnected`);
            currentClient = null;
        });
    });

    await server.listen(9000, '127.0.0.1');
    console.log("OCPP backend listening on port 9000");
    console.log("Můžeš psát příkazy typu: RemoteStartTransaction {\"idTag\":\"12345\"}");

    // Interaktivní konzole pro posílání příkazů klientovi
    rl.on('line', async (line) => {
        if (!currentClient) {
            console.log("Žádný připojený klient.");
            return;
        }

        const [method, ...rest] = line.split(' ');
        let params = {};
        try {
            params = rest.length ? JSON.parse(rest.join(' ')) : {};
        } catch (e) {
            console.log("Chyba v JSON parametrech:", e.message);
            return;
        }

        try {
            const response = await currentClient.call(method, params);
            console.log("Response:", response);
        } catch (err) {
            console.log("Chyba při volání RPC:", err);
        }
    });
}

start().catch(console.error);
