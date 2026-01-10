import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { getChargersApiV1ChargersGet } from '@/client';
import { useQuery } from '@tanstack/react-query';
import { Zap, Navigation } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { useEffect, useState, useMemo } from 'react';
import MapFilter, { MAX_POWER_LIMIT, MAX_PRICE_LIMIT, type FilterState } from '@/components/public/MapFilter';

// Fix for default marker icon in Leaflet + Vite/Webpack
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom Charger Icon
const chargerIcon = new L.DivIcon({
    className: 'bg-transparent',
    html: `<div class="w-8 h-8 bg-[#39ff14] text-black rounded-full flex items-center justify-center border-2 border-white shadow-lg shadow-[#39ff14]/50">
           <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
         </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
});

// Custom Cluster Icon
const createClusterCustomIcon = function (cluster: any) {
    return new L.DivIcon({
        html: `<div class="w-10 h-10 bg-[#39ff14] text-black rounded-full flex items-center justify-center border-2 border-white shadow-lg shadow-[#39ff14]/50 font-bold text-lg">
             <span>${cluster.getChildCount()}</span>
           </div>`,
        className: 'bg-transparent',
        iconSize: L.point(40, 40, true),
    });
}

// Controller to handle map programmatically
function MapController({ selectedCoords }: { selectedCoords: [number, number] | null }) {
    const map = useMap();

    useEffect(() => {
        if (selectedCoords) {
            map.flyTo(selectedCoords, 16, { animate: true });
        }
    }, [selectedCoords, map]);

    return null;
}

export default function PublicMap() {
    const [searchParams] = useSearchParams();
    const focusChargerId = searchParams.get('chargerId');

    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [filters, setFilters] = useState<FilterState>({
        connectorTypes: [],
        currentTypes: [],
        minPower: 0,
        maxPower: MAX_POWER_LIMIT,
        minPrice: 0,
        maxPrice: MAX_PRICE_LIMIT
    });

    const { data: chargers, isLoading } = useQuery({
        queryKey: ['chargers', 'public'],
        queryFn: async () => {
            const response = await getChargersApiV1ChargersGet();
            return response.data;
        },
    });

    // FILTERING LOGIC
    const filteredChargers = useMemo(() => {
        if (!chargers) return [];
        return chargers.filter(charger => {
            if (!charger.connectors) return false;

            // 1. Filter connectors by Type and Current Type (AC/DC)
            let relevantConnectors = charger.connectors;

            if (filters.connectorTypes.length > 0) {
                relevantConnectors = relevantConnectors.filter(c => c.type && filters.connectorTypes.includes(c.type));
            }

            if (filters.currentTypes.length > 0) {
                relevantConnectors = relevantConnectors.filter(c => c.current_type && filters.currentTypes.includes(c.current_type));
            }

            if (relevantConnectors.length === 0) return false; // No matching connectors for selected types

            // 2. Check Power & Price criteria on the relevant connectors
            // Charger is shown if it has AT LEAST ONE connector that matches both Power and Price ranges
            // (within the subset of type-matching connectors)
            const hasValidConnector = relevantConnectors.some(c => {
                const powerKw = (c.max_power_w || 0) / 1000;
                const price = typeof c.price_per_kwh === 'string' ? parseFloat(c.price_per_kwh) : (c.price_per_kwh || 0);

                const powerOk = powerKw >= filters.minPower && powerKw <= filters.maxPower;
                const priceOk = price >= filters.minPrice && price <= filters.maxPrice;

                return powerOk && priceOk;
            });

            return hasValidConnector;
        });
    }, [chargers, filters]);


    // Determine center
    let center: [number, number] = [49.8175, 15.4730];
    let selectedCoords: [number, number] | null = null;
    let initialZoom = 8;

    // Logic to find focused charger
    if (chargers && focusChargerId) {
        const target = chargers.find(c => c.id === Number(focusChargerId));
        if (target) {
            selectedCoords = [target.latitude, target.longitude];
        }
    }

    if (isLoading) {
        return <div className="flex h-full items-center justify-center">Loading map data...</div>;
    }

    return (
        <div className="h-[calc(100vh-64px)] w-full relative">
            <MapFilter
                filters={filters}
                setFilters={setFilters}
                isOpen={isFilterOpen}
                setIsOpen={setIsFilterOpen}
                onClear={() => setFilters({
                    connectorTypes: [],
                    currentTypes: [],
                    minPower: 0,
                    maxPower: MAX_POWER_LIMIT,
                    minPrice: 0,
                    maxPrice: MAX_PRICE_LIMIT
                })}
            />

            <MapContainer center={center} zoom={initialZoom} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapController selectedCoords={selectedCoords} />

                <MarkerClusterGroup chunkedLoading iconCreateFunction={createClusterCustomIcon}>
                    {filteredChargers.map((charger) => {
                        const isFocused = charger.id === Number(focusChargerId);

                        return (
                            <Marker
                                key={charger.id}
                                position={[charger.latitude, charger.longitude]}
                                icon={chargerIcon}
                                ref={(ref) => {
                                    if (ref && isFocused) {
                                        setTimeout(() => ref.openPopup(), 500);
                                    }
                                }}
                            >
                                <Popup className="min-w-[250px]">
                                    <div className="space-y-2">
                                        <h3 className="font-bold text-lg">{charger.name}</h3>
                                        <p className="text-sm text-gray-500">{charger.street} {charger.house_number}, {charger.city}</p>

                                        <div className="flex items-center gap-1 text-xs font-semibold uppercase text-primary">
                                            <Zap size={14} fill="currentColor" /> {charger.connectors?.length || 0} Connectors
                                        </div>

                                        <div className="space-y-1 mt-2">
                                            {charger.connectors?.map(c => (
                                                <div key={c.id} className="text-sm bg-gray-50 p-2.5 rounded border border-gray-100 flex flex-col gap-1">
                                                    <div className="font-bold text-base border-b border-gray-200 pb-1 mb-1 flex justify-between items-center">
                                                        <span>{c.type}</span>
                                                        <span className={`text-[10px] px-1.5 rounded ${c.current_type === 'DC' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'}`}>{c.current_type}</span>
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

                                        <a
                                            href={`https://www.google.com/maps/dir/?api=1&destination=${charger.latitude},${charger.longitude}`}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="flex items-center justify-center gap-2 w-full mt-2 bg-primary !text-white py-2 rounded-md hover:bg-primary/90 text-sm font-medium"
                                        >
                                            <Navigation size={16} /> Navigate
                                        </a>
                                    </div>
                                </Popup>
                            </Marker>
                        )
                    })}
                </MarkerClusterGroup>
            </MapContainer>
        </div>
    );
}
