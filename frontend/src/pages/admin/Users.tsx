import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getUsersApiV1UsersGet, updateUserApiV1UsersUserIdPatch, deleteUserApiV1UsersUserIdDelete } from '@/client';
import { type UserRead, type UserUpdate } from '@/client/types.gen';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Pencil, Trash2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import toast from 'react-hot-toast';

export default function UsersPage() {
    const { user: currentUser } = useAuth();
    const queryClient = useQueryClient();
    const [editingUser, setEditingUser] = useState<UserRead | null>(null);
    const [showAll, setShowAll] = useState(false);

    const { data: users, isLoading } = useQuery({
        queryKey: ['users', showAll],
        queryFn: async () => {
            const query: any = {};
            if (showAll) query.show_all = true;
            const response = await getUsersApiV1UsersGet({ query });
            return response.data;
        },
    });

    const { register, handleSubmit, setValue, watch, reset } = useForm<UserUpdate>();
    const watchedRole = watch('role');

    const updateMutation = useMutation({
        mutationFn: async ({ id, data }: { id: number, data: UserUpdate }) => {
            await updateUserApiV1UsersUserIdPatch({ path: { user_id: id }, body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            toast.success('User updated');
            setEditingUser(null);
        },
        onError: (err) => {
            toast.error('Failed to update user');
            console.error(err);
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await deleteUserApiV1UsersUserIdDelete({ path: { user_id: id } });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            toast.success('User deleted');
        }
    });

    const startEditing = (user: UserRead) => {
        setEditingUser(user);
        reset({
            name: user.name,
            email: user.email,
            role: user.role,
            balance: user.balance
        });
    };

    if (currentUser?.role !== 'admin') {
        return <div className="p-8">Access Denied. Only Admins can view this page.</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">User Management</h1>
                <div className="flex items-center space-x-2">
                    <Switch id="show-deleted-users" checked={showAll} onChange={(e) => setShowAll(e.target.checked)} />
                    <Label htmlFor="show-deleted-users">Show Deleted</Label>
                </div>
            </div>

            <Card>
                <CardContent className="p-0">
                    <div className="relative w-full overflow-auto">
                        <table className="w-full caption-bottom text-sm text-left">
                            <thead className="[&_tr]:border-b bg-gray-50/50">
                                <tr className="border-b transition-colors hover:bg-muted/50">
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground w-[100px]">ID</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">User</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Role</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Balance</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="[&_tr:last-child]:border-0">
                                {isLoading ? (
                                    <tr><td colSpan={5} className="p-4 text-center">Loading...</td></tr>
                                ) : users?.map((u) => (
                                    <tr key={u.id} className="border-b transition-colors hover:bg-muted/50">
                                        <td className="p-4 align-middle font-mono text-xs">{u.id}</td>
                                        <td className="p-4 align-middle">
                                            <div className="font-medium">{u.name}</div>
                                            <div className="text-xs text-muted-foreground">{u.email}</div>
                                        </td>
                                        <td className="p-4 align-middle">
                                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold
                                                ${u.role === 'admin' ? 'bg-red-100 text-red-800' :
                                                    u.role === 'owner' ? 'bg-purple-100 text-purple-800' :
                                                        'bg-gray-100 text-gray-800'}`}>
                                                {u.role}
                                            </span>
                                        </td>
                                        <td className="p-4 align-middle font-mono font-bold">
                                            {u.balance} CZK
                                        </td>
                                        <td className="p-4 align-middle text-right gap-2">
                                            <Button variant="ghost" size="icon" onClick={() => startEditing(u)}>
                                                <Pencil size={16} />
                                            </Button>
                                            <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                onClick={() => {
                                                    if (confirm(`Are you sure you want to delete user ${u.name}?`)) {
                                                        deleteMutation.mutate(u.id);
                                                    }
                                                }}
                                            >
                                                <Trash2 size={16} />
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            <Dialog open={!!editingUser} onOpenChange={(open) => !open && setEditingUser(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit User #{editingUser?.id}</DialogTitle>
                    </DialogHeader>
                    {editingUser && (
                        <form onSubmit={handleSubmit((data) => updateMutation.mutate({ id: editingUser.id, data }))} className="space-y-4">
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Name</Label>
                                    <Input {...register('name')} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Email</Label>
                                    <Input {...register('email')} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Role</Label>
                                    <Select
                                        value={watchedRole || editingUser.role}
                                        onValueChange={(val: any) => setValue('role', val)}
                                    >
                                        <SelectTrigger><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="user">User</SelectItem>
                                            <SelectItem value="owner">Owner</SelectItem>
                                            <SelectItem value="admin">Admin</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Balance (CZK)</Label>
                                    <Input type="number" {...register('balance', { valueAsNumber: true })} />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button type="button" variant="outline" onClick={() => setEditingUser(null)}>Cancel</Button>
                                <Button type="submit">Save Changes</Button>
                            </DialogFooter>
                        </form>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
