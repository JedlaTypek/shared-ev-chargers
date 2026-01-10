import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getCardsApiV1RfidCardsGet,
    createCardApiV1RfidCardsPost,
    deleteCardApiV1RfidCardsCardIdDelete,
    updateCardApiV1RfidCardsCardIdPatch,
    getUsersApiV1UsersGet,
    type RfidCardCreate,
    type RfidCardUpdate,
    type RfidCardRead
} from '@/client';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Trash2, Plus, CreditCard, Pencil, User, Check, ChevronsUpDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/utils/cn"

export default function CardsPage() {
    const { user: currentUser } = useAuth();
    const queryClient = useQueryClient();
    const [isAdding, setIsAdding] = useState(false);
    const [editingCard, setEditingCard] = useState<RfidCardRead | null>(null);
    const [showAll, setShowAll] = useState(false);

    // Combobox state
    const [openCombobox, setOpenCombobox] = useState(false);
    const [selectedOwnerId, setSelectedOwnerId] = useState<number | null>(null);

    const isAdmin = currentUser?.role === 'admin';

    const { data: rawCards, isLoading } = useQuery({
        queryKey: ['cards', showAll, isAdmin],
        queryFn: async () => {
            const query: any = {};
            // Admin: Toggle controls "Show Deleted" -> API parameter
            if (isAdmin && showAll) {
                query.show_all = true;
            }
            // User/Owner: Toggle controls "Show Disabled" -> Client side, so we need ALL active cards from API
            // (API by default returns all active cards, regardless of is_enabled)

            const response = await getCardsApiV1RfidCardsGet({ query });
            return response.data;
        },
    });

    // Client-side filtering
    const cards = rawCards?.filter(card => {
        if (isAdmin) return true; // Admin uses API filtering
        if (showAll) return true; // "Show Disabled" is ON, show all (active) cards
        return card.is_enabled;   // "Show Disabled" is OFF, show only enabled
    });

    const { data: users } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const response = await getUsersApiV1UsersGet();
            return response.data;
        },
        enabled: isAdmin
    });

    const { register, handleSubmit, reset } = useForm<RfidCardCreate>();

    // Edit Form
    const {
        register: regEdit,
        handleSubmit: subEdit,
        reset: resetEdit,
        setValue: setValueEdit,
        watch: watchEdit
    } = useForm<RfidCardUpdate & { owner_id?: number }>();

    const createMutation = useMutation({
        mutationFn: async (data: RfidCardCreate) => {
            await createCardApiV1RfidCardsPost({ body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cards'] });
            toast.success('Card added');
            reset();
            setIsAdding(false);
        },
        onError: (err) => {
            console.error(err);
            toast.error('Failed to add card');
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await deleteCardApiV1RfidCardsCardIdDelete({ path: { card_id: id } });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cards'] });
            toast.success('Card deleted');
        }
    });

    const updateMutation = useMutation({
        mutationFn: async ({ id, data }: { id: number, data: any }) => {
            // Casting data to any to allow owner_id if needed, though types might limit it using 'any' bypasses it
            await updateCardApiV1RfidCardsCardIdPatch({ path: { card_id: id }, body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cards'] });
            toast.success('Card updated');
            setEditingCard(null);
        },
        onError: () => {
            toast.error('Failed to update card');
        }
    });

    // Watch form values for real-time UI updates
    const watchedIsEnabled = watchEdit('is_enabled');
    const watchedIsActive = watchEdit('is_active');

    const onSubmit = (data: RfidCardCreate) => {
        createMutation.mutate({ ...data, is_active: true });
    };

    const startEditing = (card: RfidCardRead) => {
        setEditingCard(card);
        setSelectedOwnerId(card.owner_id);
        resetEdit({
            card_uid: card.card_uid,
            is_active: card.is_active,
            is_enabled: card.is_enabled, // Include is_enabled in reset
            owner_id: card.owner_id
        });
    };

    const onSaveEdit = (data: any) => {
        if (!editingCard) return;
        updateMutation.mutate({
            id: editingCard.id,
            data: {
                ...data,
                owner_id: selectedOwnerId // Ensure owner_id is passed from local state if select didn't bind well
            }
        });
    };

    // Helper to get owner name/email
    const getOwnerInfo = (ownerId: number) => {
        if (!users) return `ID: ${ownerId}`;
        const u = users.find(u => u.id === ownerId);
        return u ? `${u.name} (${u.email})` : `Unknown (ID: ${ownerId})`;
    };

    const handleEnabledChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const checked = e.target.checked;
        setValueEdit('is_enabled', checked, { shouldDirty: true, shouldTouch: true });
        // Rule: If enabling, must be active
        if (checked) {
            setValueEdit('is_active', true, { shouldDirty: true, shouldTouch: true });
        }
    };

    const handleActiveChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const checked = e.target.checked;
        setValueEdit('is_active', checked, { shouldDirty: true, shouldTouch: true });
        // Rule: If deactivating, must be disabled
        if (!checked) {
            setValueEdit('is_enabled', false, { shouldDirty: true, shouldTouch: true });
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">
                    {isAdmin ? 'All RFID Cards' : 'My RFID Cards'}
                </h1>
                <div className="flex items-center gap-4">
                    <div className="flex items-center space-x-2">
                        <Switch
                            id="show-filter"
                            checked={showAll}
                            onChange={(e) => setShowAll(e.target.checked)}
                        />
                        <Label htmlFor="show-filter">
                            {isAdmin ? 'Show Deleted' : 'Show Disabled'}
                        </Label>
                    </div>
                    <Button onClick={() => setIsAdding(!isAdding)}>
                        {isAdding ? 'Cancel' : <><Plus size={16} className="mr-2" /> Add Card</>}
                    </Button>
                </div>
            </div>

            {isAdding && (
                <Card className="mb-6 border-primary/20 bg-primary/5">
                    <CardHeader><CardTitle>Add New Card</CardTitle></CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit(onSubmit)} className="flex gap-4 items-end">
                            <div className="space-y-2 flex-1">
                                <Label>Card UID (Hex)</Label>
                                <Input placeholder="e.g. A1B2C3D4" {...register('card_uid', { required: true, minLength: 4 })} />
                            </div>
                            <Button type="submit" disabled={createMutation.isPending}>Add</Button>
                        </form>
                    </CardContent>
                </Card>
            )}

            {isLoading ? (
                <div>Loading...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {cards?.map((card) => (
                        <Card key={card.id}>
                            <CardContent className="flex flex-col gap-4 p-6">
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-full ${card.is_active ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-400'}`}>
                                            <CreditCard size={24} />
                                        </div>
                                        <div>
                                            <p className="font-mono text-lg font-bold">{card.card_uid}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className={`text-xs ${card.is_enabled ? 'text-green-600' : 'text-gray-500'}`}>
                                                    {card.is_enabled ? 'Enabled' : 'Disabled'}
                                                </span>
                                                {!card.is_active && <span className="text-xs text-red-600 border border-red-200 bg-red-50 px-1 rounded">Deleted</span>}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex gap-1">
                                        {isAdmin && (
                                            <Button variant="ghost" size="icon" onClick={() => startEditing(card)}>
                                                <Pencil size={16} />
                                            </Button>
                                        )}
                                        <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => {
                                            if (confirm('Are you sure?')) deleteMutation.mutate(card.id);
                                        }}>
                                            <Trash2 size={16} />
                                        </Button>
                                    </div>
                                </div>

                                {isAdmin && (
                                    <div className="text-xs text-muted-foreground bg-gray-50 p-2 rounded flex items-center gap-2">
                                        <User size={12} />
                                        <span className="truncate">{getOwnerInfo(card.owner_id)}</span>
                                    </div>
                                )}

                                {!isAdmin && (
                                    <div className="flex items-center justify-between pt-2 border-t">
                                        <span className="text-sm">Enabled</span>
                                        <Switch
                                            checked={card.is_enabled}
                                            onChange={(e) => updateMutation.mutate({ id: card.id, data: { is_enabled: e.target.checked } })}
                                        />
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                    {cards?.length === 0 && <p className="text-gray-500 col-span-full text-center py-10">No cards found.</p>}
                </div>
            )}

            {/* EDIT DIALOG */}
            <Dialog open={!!editingCard} onOpenChange={(open) => !open && setEditingCard(null)}>
                <DialogContent className="max-w-[400px]">
                    <DialogHeader>
                        <DialogTitle>Edit Card</DialogTitle>
                    </DialogHeader>
                    {editingCard && (
                        <form onSubmit={subEdit(onSaveEdit)} className="space-y-4">
                            <div className="space-y-2">
                                <Label>Card UID</Label>
                                <Input {...regEdit('card_uid')} />
                            </div>

                            <div className="flex items-center space-x-2">
                                <Switch
                                    id="is_enabled_edit"
                                    checked={watchedIsEnabled ?? editingCard.is_enabled}
                                    onChange={handleEnabledChange}
                                />
                                <Label htmlFor="is_enabled_edit">Enabled</Label>
                            </div>

                            {isAdmin && (
                                <div className="flex items-center space-x-2">
                                    <Switch
                                        id="is_active_edit"
                                        checked={watchedIsActive ?? editingCard.is_active}
                                        onChange={handleActiveChange}
                                    />
                                    <Label htmlFor="is_active_edit">Active (Not Deleted)</Label>
                                </div>
                            )}

                            {isAdmin && (
                                <div className="space-y-2">
                                    <Label>Owner (Search by Email)</Label>
                                    <Popover open={openCombobox} onOpenChange={setOpenCombobox} modal={true}>
                                        <PopoverTrigger asChild>
                                            <Button
                                                variant="outline"
                                                role="combobox"
                                                aria-expanded={openCombobox}
                                                className="w-full justify-between"
                                            >
                                                {selectedOwnerId
                                                    ? users?.find((u) => u.id === selectedOwnerId)?.email
                                                    : "Select owner..."}
                                                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-[300px] p-0">
                                            <Command>
                                                <CommandInput placeholder="Search user email..." />
                                                <CommandList>
                                                    <CommandEmpty>No user found.</CommandEmpty>
                                                    <CommandGroup>
                                                        {users?.map((u) => (
                                                            <CommandItem
                                                                key={u.id}
                                                                value={u.email}
                                                                onSelect={() => {
                                                                    // CommandItem value is lowercase usually?
                                                                    // We match by email
                                                                    setSelectedOwnerId(u.id);
                                                                    setValueEdit('owner_id', u.id);
                                                                    setOpenCombobox(false);
                                                                }}
                                                            >
                                                                <Check
                                                                    className={cn(
                                                                        "mr-2 h-4 w-4",
                                                                        selectedOwnerId === u.id ? "opacity-100" : "opacity-0"
                                                                    )}
                                                                />
                                                                {u.email} ({u.name})
                                                            </CommandItem>
                                                        ))}
                                                    </CommandGroup>
                                                </CommandList>
                                            </Command>
                                        </PopoverContent>
                                    </Popover>
                                </div>
                            )}

                            <DialogFooter>
                                <Button type="button" variant="outline" onClick={() => setEditingCard(null)}>Cancel</Button>
                                <Button type="submit">Save Changes</Button>
                            </DialogFooter>
                        </form>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
