import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateUserApiV1UsersUserIdPatch } from '@/client';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { Check, ShieldCheck, Zap } from 'lucide-react';

export default function BecomeOwnerPage() {
    const { user, refreshUser } = useAuth(); // Assuming refreshUser exists in context to reload profile
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const upgradeMutation = useMutation({
        mutationFn: async () => {
            if (!user) throw new Error("No user logged in");
            await updateUserApiV1UsersUserIdPatch({
                path: { user_id: user.id },
                body: { role: 'owner' }
            });
        },
        onSuccess: async () => {
            toast.success("Congratulations! You are now a Charger Owner.");
            await refreshUser(); // Reload user data to update role in context
            queryClient.invalidateQueries({ queryKey: ['users', 'me'] });
            navigate('/admin/dashboard'); // Redirect to dashboard or relevant page
        },
        onError: (err) => {
            console.error(err);
            toast.error("Failed to upgrade role. Please try again.");
        }
    });

    return (
        <div className="container mx-auto max-w-2xl py-10 px-4">
            <Card className="border-primary/20">
                <CardHeader className="text-center pb-2">
                    <div className="mx-auto bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mb-4 text-primary">
                        <Zap size={32} />
                    </div>
                    <CardTitle className="text-3xl font-bold text-primary">Become a Charger Owner</CardTitle>
                    <CardDescription className="text-lg mt-2">
                        Share your EV charger with the community and earn money.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8 pt-6">
                    <div className="grid gap-4">
                        <div className="flex items-start gap-3">
                            <div className="mt-1 bg-green-100 text-green-700 p-1 rounded-full"><Check size={16} /></div>
                            <div>
                                <h3 className="font-semibold">Earn Passive Income</h3>
                                <p className="text-sm text-gray-500">Set your own price per kWh and get paid securely.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <div className="mt-1 bg-green-100 text-green-700 p-1 rounded-full"><Check size={16} /></div>
                            <div>
                                <h3 className="font-semibold">Full Control</h3>
                                <p className="text-sm text-gray-500">Manage availability, view transaction history, and detailed stats.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <div className="mt-1 bg-green-100 text-green-700 p-1 rounded-full"><Check size={16} /></div>
                            <div>
                                <h3 className="font-semibold">Help the Community</h3>
                                <p className="text-sm text-gray-500">Expand the charging network and support sustainable transport.</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border text-sm text-gray-600 dark:text-gray-300">
                        <div className="flex items-center gap-2 font-semibold mb-2">
                            <ShieldCheck size={16} className="text-white" />
                            <span>Terms and Conditions</span>
                        </div>
                        <p>
                            By clicking "Start Sharing", you agree to our Platform Terms of Service.
                            You confirm that you own the charger you intend to share and you are authorized to operate it.
                            We charge a small platform fee on each transaction.
                        </p>
                    </div>

                    <Button
                        size="lg"
                        className="w-full text-lg font-bold shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all"
                        onClick={() => upgradeMutation.mutate()}
                        disabled={upgradeMutation.isPending}
                    >
                        {upgradeMutation.isPending ? "Processing..." : "I Agree - Start Sharing"}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
