import React, { createContext, useContext, useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
    loginAccessTokenApiV1LoginAccessTokenPost,
    readUserMeApiV1UsersMeGet,
    type UserRead,
    type BodyLoginAccessTokenApiV1LoginAccessTokenPost
} from '../client';
import toast from 'react-hot-toast';

interface AuthContextType {
    user: UserRead | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (data: BodyLoginAccessTokenApiV1LoginAccessTokenPost) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
    const queryClient = useQueryClient();

    // Fetch current user if token exists
    const { data: userResponse, isLoading: isUserLoading, isError, error } = useQuery({
        queryKey: ['me'],
        queryFn: async () => {
            try {
                console.log("Fetching user/me...");
                const response = await readUserMeApiV1UsersMeGet();
                console.log("Fetch user/me success:", response);
                return response;
            } catch (err: any) {
                console.error("Fetch user/me failed:", err);
                // Log full error details
                if (err.response) {
                    console.error("Response data:", err.response.data);
                    console.error("Response status:", err.response.status);
                    console.error("Response headers:", err.response.headers);
                } else if (err.request) {
                    console.error("Request made but no response:", err.request);
                } else {
                    console.error("Error message:", err.message);
                }
                throw err;
            }
        },
        enabled: !!token,
        retry: false,
    });

    const user = userResponse?.data;

    // If fetching user fails (e.g. invalid token), logout
    useEffect(() => {
        if (isError) {
            console.warn("User fetch failed, logging out. Error:", error);
            logout();
        }
    }, [isError, error]);

    const login = async (credentials: BodyLoginAccessTokenApiV1LoginAccessTokenPost) => {
        try {
            const response = await loginAccessTokenApiV1LoginAccessTokenPost({ body: credentials });
            const accessToken = response.data?.access_token;

            if (!accessToken) throw new Error("No access token received");

            localStorage.setItem('access_token', accessToken);
            setToken(accessToken);

            // Invalidate query to fetch user immediately
            await queryClient.invalidateQueries({ queryKey: ['me'] });

            toast.success('Logged in successfully');
        } catch (error) {
            console.error("Login Error:", error);
            toast.error('Login failed. Please check your credentials.');
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setToken(null);
        queryClient.setQueryData(['me'], null);
        queryClient.clear();
        toast.success('Logged out');
    };

    const refreshUser = async () => {
        await queryClient.invalidateQueries({ queryKey: ['me'] });
    };

    const value = {
        user: user ?? null,
        isLoading: isUserLoading && !!token,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
// End of AuthContext
