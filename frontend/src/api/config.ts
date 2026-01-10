import { client } from '../client/client.gen';

// 1. Configure the auto-generated client
client.setConfig({
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
});

// 2. Interceptor for Auth
client.interceptors.request.use((request: any) => {
    const token = localStorage.getItem('access_token');
    // Exclude login endpoint, as sending an invalid token there crashes the backend
    if (token && !request.url?.includes('login/access-token')) {
        // Safe check for headers object vs instance
        if (!request.headers) {
            request.headers = {};
        }

        // Check if .set exists (AxiosHeaders) or just assign property
        if (typeof request.headers.set === 'function') {
            request.headers.set('Authorization', `Bearer ${token}`);
        } else {
            request.headers['Authorization'] = `Bearer ${token}`;
        }

        console.log("Attaching token to request:", request.url);
    }
    return request;
});
