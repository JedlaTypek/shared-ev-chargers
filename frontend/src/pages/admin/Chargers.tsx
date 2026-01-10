import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getChargersApiV1ChargersGet,
    createChargerApiV1ChargersPost,
    deleteChargerApiV1ChargersChargerIdDelete,
    updateChargerApiV1ChargersChargerIdPatch,
    updateConnectorApiV1ConnectorsConnectorIdPatch,
    type ChargerCreate,
    type ChargerUpdate,
    type ChargerRead,
    type ConnectorRead,
    type ConnectorUpdate
} from '@/client';
import { useAuth } from '@/context/AuthContext';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Plus, Zap, Trash2, Pencil, Settings2, ScrollText, Copy } from 'lucide-react';
import toast from 'react-hot-toast';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import LocationPicker from '@/components/admin/LocationPicker';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

interface Props {
    mode?: 'mine' | 'all';
}

export default function ChargersPage({ mode = 'mine' }: Props) {
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const [isAdding, setIsAdding] = useState(false);
    const [showAll, setShowAll] = useState(false);
    const [editingChargerId, setEditingChargerId] = useState<number | null>(null);
    const [editingConnector, setEditingConnector] = useState<ConnectorRead | null>(null);

    // --- CREATE ---
    const { register: regCreate, handleSubmit: subCreate, setValue, watch, formState: { errors } } = useForm<ChargerCreate>();

    const watchedLat = watch('latitude');
    const watchedLon = watch('longitude');

    // --- EDIT CHARGER ---
    const {
        register: regEdit,
        handleSubmit: subEdit,
        setValue: setValueEdit,
        watch: watchEdit,
        reset: resetEdit
    } = useForm<ChargerUpdate>();

    const watchedLatEdit = watchEdit('latitude');
    const watchedLonEdit = watchEdit('longitude');

    // --- EDIT CONNECTOR ---
    const {
        register: regConn,
        handleSubmit: subConn,
        setValue: setValueConn,
        reset: resetConn,
        watch: watchConn
    } = useForm<ConnectorUpdate>();

    const watchedType = watchConn('type');
    const watchedCurrentType = watchConn('current_type');

    const { data: chargers } = useQuery({
        queryKey: ['chargers', mode, showAll],
        queryFn: async () => {
            const query: any = mode === 'mine' ? { mine: true } : {};
            if (showAll) query.show_all = true;

            // Cast query to any to bypass TS check if generated client types are not yet updated
            const response = await getChargersApiV1ChargersGet({ query: query as any });
            return response.data;
        },
    });

    // ... mutations ... (unchanged)

    const createMutation = useMutation({
        mutationFn: async (data: ChargerCreate) => {
            await createChargerApiV1ChargersPost({ body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['chargers'] });
            toast.success('Charger created');
            setIsAdding(false);
        }
    });

    const updateMutation = useMutation({
        mutationFn: async ({ id, data }: { id: number, data: ChargerUpdate }) => {
            await updateChargerApiV1ChargersChargerIdPatch({ path: { charger_id: id }, body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['chargers'] });
            toast.success('Charger updated');
            setEditingChargerId(null);
            resetEdit();
        }
    });

    const updateConnectorMutation = useMutation({
        mutationFn: async ({ id, data }: { id: number, data: ConnectorUpdate }) => {
            await updateConnectorApiV1ConnectorsConnectorIdPatch({ path: { connector_id: id }, body: data });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['chargers'] });
            toast.success('Connector updated');
            setEditingConnector(null);
            resetConn();
        }
    });

    // --- DELETE ---
    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await deleteChargerApiV1ChargersChargerIdDelete({ path: { charger_id: id } });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['chargers'] });
            toast.success('Charger deleted');
        }
    });

    const startEditing = (charger: ChargerRead) => {
        setEditingChargerId(charger.id);
        resetEdit({
            name: charger.name,
            street: charger.street,
            house_number: charger.house_number,
            city: charger.city,
            postal_code: charger.postal_code,
            region: charger.region,
            latitude: charger.latitude,
            longitude: charger.longitude,
            is_active: charger.is_active
        });
        setIsAdding(false);
    };

    const startEditingConnector = (connector: ConnectorRead) => {
        setEditingConnector(connector);
        resetConn({
            type: connector.type,
            current_type: connector.current_type,
            max_power_w: connector.max_power_w,
            price_per_kwh: connector.price_per_kwh,
            is_active: connector.is_active
        });
    };

    if (user?.role !== 'owner' && user?.role !== 'admin') {
        return <div>Access Denied. Become an Owner to manage chargers.</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">{mode === 'all' ? 'All Chargers' : 'My Chargers'}</h1>
                <div className="flex items-center gap-4">
                    {user?.role === 'admin' && (
                        <div className="flex items-center space-x-2">
                            <Switch id="show-deleted" checked={showAll} onChange={(e) => setShowAll(e.target.checked)} />
                            <Label htmlFor="show-deleted">Show Deleted</Label>
                        </div>
                    )}
                    <Button onClick={() => { setIsAdding(!isAdding); setEditingChargerId(null); }}>
                        {isAdding ? 'Cancel' : <><Plus size={16} className="mr-2" /> Add Charger</>}
                    </Button>
                </div>
            </div>

            {/* CREATE CHARGER DIALOG */}
            <Dialog open={isAdding} onOpenChange={(open: boolean) => setIsAdding(open)}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Register New Charger</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={subCreate((data) => createMutation.mutate({ ...data, is_active: true }))} className="space-y-4">
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <Input placeholder="Charger Name" {...regCreate('name', { required: true })} />
                                <Input placeholder="Region (Kraj)" {...regCreate('region')} />
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                                <Input placeholder="Street" {...regCreate('street')} />
                                <Input placeholder="House No." {...regCreate('house_number')} />
                                <Input placeholder="City" {...regCreate('city')} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Input placeholder="Postal Code" {...regCreate('postal_code')} />
                            </div>

                            <div className="space-y-2">
                                <h3 className="text-sm font-medium">Location</h3>
                                <LocationPicker
                                    latitude={watchedLat}
                                    longitude={watchedLon}
                                    onLocationSelect={(lat, lng) => {
                                        setValue('latitude', lat);
                                        setValue('longitude', lng);
                                    }}
                                />
                                <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground bg-gray-50 p-2 rounded">
                                    <div>Latitude: {watchedLat?.toFixed(6) || 'Not selected'}</div>
                                    <div>Longitude: {watchedLon?.toFixed(6) || 'Not selected'}</div>
                                    <input type="hidden" {...regCreate('latitude', { required: true, valueAsNumber: true })} />
                                    <input type="hidden" {...regCreate('longitude', { required: true, valueAsNumber: true })} />
                                </div>
                                {errors.latitude && <p className="text-red-500 text-xs">Location is required</p>}
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setIsAdding(false)}>Cancel</Button>
                            <Button type="submit">Create Charger</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* CHARGER LIST */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {chargers?.map((charger) => {
                    return (
                        <Card key={charger.id}>
                            <CardHeader className="flex flex-row items-start justify-between pb-2">
                                <div>
                                    <CardTitle className="text-lg flex items-center gap-2">
                                        {charger.name}
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${charger.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                            {charger.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </CardTitle>
                                    <CardDescription>{charger.city}, {charger.street} {charger.house_number}</CardDescription>
                                </div>
                                <div className="flex gap-1">
                                    <Link to={`/admin/history?chargerId=${charger.id}&view=charger_logs`}>
                                        <Button variant="ghost" size="icon" title="View Logs">
                                            <ScrollText size={16} />
                                        </Button>
                                    </Link>
                                    <Button variant="ghost" size="icon" onClick={() => startEditing(charger)}>
                                        <Pencil size={16} />
                                    </Button>
                                    <Button variant="ghost" size="icon" onClick={() => deleteMutation.mutate(charger.id)}>
                                        <Trash2 size={16} className="text-red-500" />
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="text-xs text-muted-foreground mb-4 space-y-1">
                                    <div className="mb-1 font-semibold">OCPP ID:</div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="text-xs font-mono bg-slate-100 border border-slate-200 text-slate-600 px-2 py-1 rounded truncate max-w-[220px]" title={charger.ocpp_id}>
                                            {charger.ocpp_id}
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="icon"
                                            className="h-6 w-6"
                                            onClick={() => {
                                                navigator.clipboard.writeText(charger.ocpp_id);
                                                toast.success('OCPP ID copied');
                                            }}
                                            title="Copy OCPP ID"
                                        >
                                            <Copy size={12} />
                                        </Button>
                                    </div>

                                    <div className="mb-1 font-semibold">OCPP Connection URL:</div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="text-[10px] font-mono bg-slate-100 border border-slate-200 text-slate-600 px-2 py-1 rounded truncate max-w-[220px]" title={`wss://jedlickaf.cz/${charger.ocpp_id}`}>
                                            wss://jedlickaf.cz/{charger.ocpp_id}
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="icon"
                                            className="h-6 w-6"
                                            onClick={() => {
                                                navigator.clipboard.writeText(`wss://jedlickaf.cz/${charger.ocpp_id}`);
                                                toast.success('OCPP URL copied');
                                            }}
                                            title="Copy OCPP URL"
                                        >
                                            <Copy size={12} />
                                        </Button>
                                    </div>

                                    {charger.firmware_version && <div>Firmware version: {charger.firmware_version}</div>}
                                    {charger.model && <div>Model: {charger.model}</div>}
                                </div>

                                <h4 className="font-semibold text-sm mb-2 flex items-center gap-1"><Zap size={14} /> Connectors ({charger.connectors?.length})</h4>
                                <div className="space-y-2">
                                    {charger.connectors?.map(c => (
                                        <div key={c.id} className="flex justify-between items-start text-sm p-3 border rounded bg-gray-50/50">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold text-base">{c.type}</span>
                                                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded ${c.current_type === 'DC' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                                        {c.current_type}
                                                    </span>
                                                    <span className="text-gray-400 font-mono text-xs">#{c.ocpp_number}</span>
                                                </div>
                                                <div className="flex gap-4 text-xs text-muted-foreground">
                                                    <span>Max: <b>{c.max_power_w ? `${c.max_power_w / 1000} kW` : '-'}</b></span>
                                                    <span>Price: <b>{c.price_per_kwh} CZK/kWh</b></span>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                                <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={() => startEditingConnector(c)}>
                                                    <Settings2 size={14} />
                                                </Button>
                                                <div className="text-xs">
                                                    {c.status}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {!charger.connectors?.length && <p className="text-xs text-gray-400">No connectors connected yet.</p>}
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* EDIT CHARGER DIALOG */}
            <Dialog open={!!editingChargerId} onOpenChange={(open: boolean) => !open && setEditingChargerId(null)}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Edit Charger</DialogTitle>
                    </DialogHeader>
                    {editingChargerId && (
                        <form onSubmit={subEdit((data) => updateMutation.mutate({ id: editingChargerId, data }))} className="space-y-4">
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <Label>Name</Label>
                                        <Input placeholder="Charger Name" {...regEdit('name', { required: true })} />
                                    </div>
                                    <div className="space-y-1">
                                        <Label>Region</Label>
                                        <Input placeholder="Region (Kraj)" {...regEdit('region')} />
                                    </div>
                                </div>
                                <div className="grid grid-cols-3 gap-4">
                                    <Input placeholder="Street" {...regEdit('street')} />
                                    <Input placeholder="House No." {...regEdit('house_number')} />
                                    <Input placeholder="City" {...regEdit('city')} />
                                </div>
                                <Input placeholder="Postal Code" {...regEdit('postal_code')} />

                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Location</h3>
                                    <LocationPicker
                                        latitude={watchedLatEdit || undefined} // fallback undefined if null
                                        longitude={watchedLonEdit || undefined}
                                        onLocationSelect={(lat, lng) => {
                                            setValueEdit('latitude', lat);
                                            setValueEdit('longitude', lng);
                                        }}
                                    />
                                    <div className="text-xs flex gap-4 text-muted-foreground">
                                        <span>Lat: {watchedLatEdit?.toFixed(6)}</span>
                                        <span>Lng: {watchedLonEdit?.toFixed(6)}</span>
                                    </div>
                                    <input type="hidden" {...regEdit('latitude', { valueAsNumber: true })} />
                                    <input type="hidden" {...regEdit('longitude', { valueAsNumber: true })} />
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Checkbox
                                        id="is_active_charger"
                                        defaultChecked={chargers?.find(c => c.id === editingChargerId)?.is_active || false}
                                        onCheckedChange={(checked: boolean | 'indeterminate') => setValueEdit('is_active', checked === true)}
                                    />
                                    <Label htmlFor="is_active_charger">Charger is Active</Label>
                                </div>
                            </div>
                            <DialogFooter>
                                <Button type="button" variant="outline" onClick={() => setEditingChargerId(null)}>Cancel</Button>
                                <Button type="submit">Save Changes</Button>
                            </DialogFooter>
                        </form>
                    )}
                </DialogContent>
            </Dialog>

            {/* CONNECTOR EDIT DIALOG */}
            <Dialog open={!!editingConnector} onOpenChange={(open: boolean) => !open && setEditingConnector(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit Connector #{editingConnector?.ocpp_number}</DialogTitle>
                    </DialogHeader>
                    {editingConnector && (
                        <form onSubmit={subConn((data) => updateConnectorMutation.mutate({ id: editingConnector.id, data }))} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Connector Type</Label>
                                    <Select
                                        value={watchedType || editingConnector.type || undefined}
                                        onValueChange={(val: any) => setValueConn('type', val)}
                                    >
                                        <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="Type2">Type 2 (AC)</SelectItem>
                                            <SelectItem value="CCS">CCS (DC)</SelectItem>
                                            <SelectItem value="CHAdeMO">CHAdeMO (DC)</SelectItem>
                                            <SelectItem value="Tesla">Tesla</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Current Type</Label>
                                    <Select
                                        value={watchedCurrentType || editingConnector.current_type || undefined}
                                        onValueChange={(val: any) => setValueConn('current_type', val)}
                                    >
                                        <SelectTrigger><SelectValue placeholder="AC/DC" /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="AC">AC</SelectItem>
                                            <SelectItem value="DC">DC</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Max Power (Watts)</Label>
                                    <Input
                                        type="number"
                                        {...regConn('max_power_w', { valueAsNumber: true })}
                                        placeholder="e.g. 22000"
                                    />
                                    <p className="text-[10px] text-muted-foreground">Type in Watts (22kW = 22000)</p>
                                </div>
                                <div className="space-y-2">
                                    <Label>Price (CZK/kWh)</Label>
                                    <Input
                                        type="number"
                                        step="0.1"
                                        {...regConn('price_per_kwh', { valueAsNumber: true })}
                                        placeholder="e.g. 10.5"
                                    />
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="is_active_conn"
                                    defaultChecked={editingConnector.is_active || false}
                                    onCheckedChange={(checked: boolean | 'indeterminate') => setValueConn('is_active', checked === true)}
                                />
                                <Label htmlFor="is_active_conn">Enabled (Is Active)</Label>
                            </div>

                            <DialogFooter>
                                <Button type="button" variant="outline" onClick={() => setEditingConnector(null)}>Cancel</Button>
                                <Button type="submit">Save Changes</Button>
                            </DialogFooter>
                        </form>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
