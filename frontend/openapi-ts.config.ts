import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
    client: '@hey-api/client-axios',
    input: 'http://127.0.0.1:3000/api/v1/openapi.json',
    output: {
        format: 'prettier',
        path: 'src/client',
    },
});
