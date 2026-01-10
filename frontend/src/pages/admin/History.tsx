import { useQuery } from '@tanstack/react-query';
import {
    getMyTransactionsApiV1TransactionsGet,
    getChargersApiV1ChargersGet,
    getCardsApiV1RfidCardsGet,
    type ChargerRead
} from '@/client';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useState } from 'react';
import { Zap, MapPin, Navigation, Map } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Link, useSearchParams } from 'react-router-dom';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

export default function HistoryPage() {
    const { user } = useAuth();
    const isAdmin = user?.role === 'admin';
    const [searchParams, setSearchParams] = useSearchParams();
    const [selectedCharger, setSelectedCharger] = useState<ChargerRead | null>(null);
    const view = searchParams.get('view') || 'my_charges';
    const chargerIdParam = searchParams.get('chargerId');
    const filteredChargerId = chargerIdParam && chargerIdParam !== 'all' ? parseInt(chargerIdParam) : null;

    // Determine query parameters based on view
    const isChargerUsageView = view === 'charger_logs';

    const { data: logs, isLoading: logsLoading } = useQuery({
        queryKey: ['history', view, filteredChargerId],
        queryFn: async () => {
            const query: any = {};
            if (isChargerUsageView) {
                query.as_owner = true;
                if (filteredChargerId) {
                    query.charger_id = filteredChargerId;
                }
            }
            // For standard 'my_charges', no special params needed (defaults to my user_id)

            const response = await getMyTransactionsApiV1TransactionsGet({ query });
            return response.data;
        },
    });

    // Fetch all chargers we can see to map IDs to names
    const { data: chargers } = useQuery({
        queryKey: ['chargers', 'all'],
        queryFn: async () => {
            // If owner viewing usage, they might want to filter by their chargers. 
            // Admin sees all.
            const response = await getChargersApiV1ChargersGet({ query: { mine: !isAdmin } });
            return response.data;
        },
    });

    const { data: cards } = useQuery({
        queryKey: ['cards', isAdmin],
        queryFn: async () => {
            const response = await getCardsApiV1RfidCardsGet({ query: { show_all: isAdmin } });
            return response.data;
        },
    });

    const getCharger = (id: number | null) => chargers?.find(c => c.id === id);
    const getCardUid = (id: number | null) => {
        if (!id) return '-';
        const card = cards?.find(c => c.id === id);
        return card ? card.card_uid : `ID: ${id}`;
    };

    const handleChargerFilterChange = (value: string) => {
        const newParams = new URLSearchParams(searchParams);
        if (value && value !== 'all') {
            newParams.set('chargerId', value);
        } else {
            newParams.delete('chargerId');
        }
        setSearchParams(newParams);
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center flex-wrap gap-4">
                <h1 className="text-2xl font-bold">
                    {isChargerUsageView ? 'Charger Usage History' : 'My Charging History'}
                </h1>

                {isChargerUsageView && (
                    <div className="w-[250px]">
                        <Select
                            value={chargerIdParam || 'all'}
                            onValueChange={handleChargerFilterChange}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="All Chargers" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Chargers</SelectItem>
                                {chargers?.map((c) => (
                                    <SelectItem key={c.id} value={c.id.toString()}>
                                        {c.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                )}
            </div>

            <Card>
                <CardContent className="p-0">
                    {logsLoading ? <div className="p-4">Loading...</div> : (
                        <div className="relative w-full overflow-auto">
                            <table className="w-full caption-bottom text-sm text-left">
                                <thead className="[&_tr]:border-b">
                                    <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Date</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Charger</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">RFID Card</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Duration</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Energy</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Price</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="[&_tr:last-child]:border-0">
                                    {logs?.map((log) => {
                                        const charger = getCharger(log.charger_id);
                                        return (
                                            <tr key={log.id} className="border-b transition-colors hover:bg-muted/50">
                                                <td className="p-4 align-middle whitespace-nowrap">{new Date(log.start_time).toLocaleString()}</td>
                                                <td className="p-4 align-middle font-medium">
                                                    {charger ? (
                                                        <button
                                                            onClick={() => setSelectedCharger(charger)}
                                                            className="text-primary hover:underline focus:outline-none"
                                                        >
                                                            {charger.name}
                                                        </button>
                                                    ) : (
                                                        <span className="text-muted-foreground">Unknown (ID: {log.charger_id})</span>
                                                    )}
                                                </td>
                                                <td className="p-4 align-middle font-mono text-xs">
                                                    {getCardUid(log.rfid_card_id)}
                                                </td>
                                                <td className="p-4 align-middle">
                                                    {log.end_time ?
                                                        Math.round((new Date(log.end_time).getTime() - new Date(log.start_time).getTime()) / 60000) + ' min'
                                                        : '-'}
                                                </td>
                                                <td className="p-4 align-middle font-mono">{log.energy_wh ? (log.energy_wh / 1000).toFixed(2) + ' kWh' : '-'}</td>
                                                <td className="p-4 align-middle font-bold">{log.price ? log.price + ' CZK' : '-'}</td>
                                                <td className="p-4 align-middle">
                                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${log.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                        log.status === 'running' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100'
                                                        }`}>
                                                        {log.status}
                                                    </span>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                    {!logs?.length && (
                                        <tr><td colSpan={7} className="p-4 text-center text-gray-500">No history found</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>


            {/* CHARGER DETAIL DIALOG */}
            <Dialog open={!!selectedCharger} onOpenChange={(open) => !open && setSelectedCharger(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Charger Details</DialogTitle>
                    </DialogHeader>
                    {selectedCharger && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <div className="p-3 bg-primary/10 rounded-full text-primary">
                                    <Zap size={24} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg">{selectedCharger.name}</h3>
                                    <div className="flex items-center text-sm text-muted-foreground">
                                        <MapPin size={14} className="mr-1" />
                                        {selectedCharger.city}, {selectedCharger.street} {selectedCharger.house_number}
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-muted-foreground block">Status</span>
                                    <span className={selectedCharger.is_active ? "text-green-600 font-medium" : "text-gray-500"}>
                                        {selectedCharger.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground block">OCPP ID</span>
                                    <span className="font-mono">{selectedCharger.ocpp_id}</span>
                                </div>
                            </div>

                            <div className="space-y-2 pt-2 border-t">
                                <h4 className="font-semibold text-sm flex items-center gap-1">
                                    <Zap size={14} fill="currentColor" className="text-primary" />
                                    Connectors ({selectedCharger.connectors?.length || 0})
                                </h4>
                                {selectedCharger.connectors?.map(c => (
                                    <div key={c.id} className="text-sm bg-gray-50 p-2.5 rounded border border-gray-100 flex flex-col gap-1">
                                        <div className="font-bold text-xs border-b border-gray-200 pb-1 mb-1 flex justify-between items-center">
                                            <span>{c.type}</span>
                                            <span className={`text-[10px] px-1.5 rounded ${c.current_type === 'DC' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                                {c.current_type}
                                            </span>
                                        </div>
                                        <div className="flex justify-between text-xs">
                                            <span className="text-gray-500">Power:</span>
                                            <span className="font-mono font-medium">{c.max_power_w ? `${c.max_power_w / 1000} kW` : '-'}</span>
                                        </div>
                                        <div className="flex justify-between text-xs">
                                            <span className="text-gray-500">Price:</span>
                                            <span className="font-bold text-primary">{c.price_per_kwh} CZK/kWh</span>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="grid grid-cols-2 gap-2 mt-4">
                                <Link
                                    to={`/map?chargerId=${selectedCharger.id}`}
                                    target="_blank"
                                    className="flex items-center justify-center gap-2 bg-secondary text-secondary-foreground py-2.5 rounded-md hover:bg-secondary/80 text-sm font-medium transition-colors"
                                >
                                    <Map size={16} /> Show on Map
                                </Link>
                                <a
                                    href={`https://www.google.com/maps/dir/?api=1&destination=${selectedCharger.latitude},${selectedCharger.longitude}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="flex items-center justify-center gap-2 bg-primary text-white py-2.5 rounded-md hover:bg-primary/90 text-sm font-medium transition-colors"
                                >
                                    <Navigation size={16} /> Navigate
                                </a>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
