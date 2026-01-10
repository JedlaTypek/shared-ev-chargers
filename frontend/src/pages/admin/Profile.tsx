import { useAuth } from '@/context/AuthContext';
import { useForm, Controller } from 'react-hook-form';
import { updateUserApiV1UsersUserIdPatch, type UserUpdate } from '@/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import toast from 'react-hot-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export default function ProfilePage() {
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const isAdmin = user?.role === 'admin';

    const { register, handleSubmit, control } = useForm<UserUpdate>({
        defaultValues: {
            name: user?.name,
            email: user?.email,
            role: user?.role,
            balance: user?.balance
        }
    });

    const mutation = useMutation({
        mutationFn: async (data: UserUpdate) => {
            if (!user) return;
            await updateUserApiV1UsersUserIdPatch({ path: { user_id: user.id }, body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['me'] });
            toast.success('Profile updated');
        },
        onError: () => toast.error('Failed to update profile')
    });

    const onSubmit = (data: UserUpdate) => {
        const cleanData: UserUpdate = {};

        // Only include fields that are present and not empty/unchanged
        if (data.name && data.name !== user?.name) cleanData.name = data.name;
        if (data.email && data.email !== user?.email) cleanData.email = data.email;

        // Admin only fields
        if (isAdmin) {
            if (data.role && data.role !== user?.role) cleanData.role = data.role;
            if (data.balance !== undefined && data.balance != user?.balance) cleanData.balance = Number(data.balance);
        }

        // Handle password fields - only send if non-empty
        if (data.password) cleanData.password = data.password;
        if (data.old_password) cleanData.old_password = data.old_password;

        if (Object.keys(cleanData).length === 0) {
            toast('No changes to save');
            return;
        }

        mutation.mutate(cleanData);
    };

    if (!user) return <div>Loading...</div>;

    return (
        <div className="max-w-xl">
            <h1 className="text-2xl font-bold mb-6">User Profile</h1>
            <Card>
                <CardHeader><CardTitle>My Details</CardTitle></CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Role</Label>
                                {isAdmin ? (
                                    <Controller
                                        control={control}
                                        name="role"
                                        render={({ field }) => (
                                            <Select onValueChange={field.onChange} defaultValue={field.value || undefined}>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select role" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="user">User</SelectItem>
                                                    <SelectItem value="owner">Owner</SelectItem>
                                                    <SelectItem value="admin">Admin</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        )}
                                    />
                                ) : (
                                    <Input disabled value={user.role} className="bg-gray-50 uppercase font-bold" />
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label>Balance (CZK)</Label>
                                {isAdmin ? (
                                    <Input type="number" step="0.1" {...register('balance')} />
                                ) : (
                                    <Input disabled value={`${user.balance} CZK`} className="bg-gray-50" />
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Name</Label>
                            <Input {...register('name')} />
                        </div>

                        <div className="space-y-2">
                            <Label>Email</Label>
                            <Input {...register('email')} />
                        </div>

                        <div className="pt-4 border-t mt-4">
                            <h3 className="font-semibold mb-3">Change Password</h3>
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Old Password</Label>
                                    <Input type="password" placeholder="Required for password change" {...register('old_password')} />
                                </div>
                                <div className="space-y-2">
                                    <Label>New Password</Label>
                                    <Input type="password" placeholder="Leave blank to keep current" {...register('password')} />
                                </div>
                            </div>
                        </div>

                        <Button type="submit" disabled={mutation.isPending}>
                            {mutation.isPending ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
