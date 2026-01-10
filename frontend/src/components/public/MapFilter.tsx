import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

import type { ConnectorType, CurrentType } from "@/client";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MapFilterProps {
    filters: FilterState;
    setFilters: (filters: FilterState) => void;
    // Helper to clear filters or defaults
    onClear?: () => void;
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
}

export interface FilterState {
    connectorTypes: ConnectorType[];
    currentTypes: CurrentType[];
    minPower: number; // in kW
    maxPower: number; // in kW
    minPrice: number; // CZK/kWh
    maxPrice: number; // CZK/kWh
}

const ALL_CONNECTOR_TYPES: ConnectorType[] = ['Type1', 'Type2', 'CCS', 'CHAdeMO', 'Tesla'];
const ALL_CURRENT_TYPES: CurrentType[] = ['AC', 'DC'];
export const MAX_POWER_LIMIT = 350; // 350 kW
export const MAX_PRICE_LIMIT = 50;  // 50 CZK

export default function MapFilter({ filters, setFilters, onClear, isOpen, setIsOpen }: MapFilterProps) {

    const toggleConnectorType = (type: ConnectorType) => {
        const current = filters.connectorTypes;
        if (current.includes(type)) {
            setFilters({ ...filters, connectorTypes: current.filter(t => t !== type) });
        } else {
            setFilters({ ...filters, connectorTypes: [...current, type] });
        }
    };

    const toggleCurrentType = (type: CurrentType) => {
        const current = filters.currentTypes;
        if (current.includes(type)) {
            setFilters({ ...filters, currentTypes: current.filter(t => t !== type) });
        } else {
            setFilters({ ...filters, currentTypes: [...current, type] });
        }
    };

    const handlePowerChange = (vals: number[]) => {
        setFilters({ ...filters, minPower: vals[0], maxPower: vals[1] });
    };

    const handlePriceChange = (vals: number[]) => {
        setFilters({ ...filters, minPrice: vals[0], maxPrice: vals[1] });
    };

    if (!isOpen) {
        return (
            <div className="absolute bottom-6 left-4 z-[500]">
                <Button onClick={() => setIsOpen(true)} className="bg-white text-black hover:bg-gray-100 shadow-xl border border-gray-200">
                    <Filter size={16} className="mr-2" /> Filters
                </Button>
            </div>
        );
    }

    return (
        <div className="absolute bottom-6 left-4 z-[500] w-80 bg-white shadow-xl rounded-lg border border-gray-200 flex flex-col max-h-[calc(100vh-120px)] overflow-y-auto">
            <div className="p-4 border-b flex justify-between items-center sticky top-0 bg-white z-10">
                <h3 className="font-semibold text-lg flex items-center gap-2"><Filter size={18} /> Filters</h3>
                <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                    <X size={18} />
                </Button>
            </div>

            <div className="p-4 space-y-6">
                {/* CONNECTOR TYPES */}
                <div className="space-y-3">
                    <Label className="text-base">Connector Types</Label>
                    <div className="grid grid-cols-2 gap-2">
                        {ALL_CONNECTOR_TYPES.map(type => (
                            <div key={type} className="flex items-center space-x-2">
                                <Checkbox
                                    id={`filter-${type}`}
                                    checked={filters.connectorTypes.includes(type)}
                                    onCheckedChange={() => toggleConnectorType(type)}
                                />
                                <Label htmlFor={`filter-${type}`} className="text-sm font-normal cursor-pointer">
                                    {type}
                                </Label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="border-t"></div>

                {/* CURRENT TYPES (AC/DC) */}
                <div className="space-y-3">
                    <Label className="text-base">Current Type</Label>
                    <div className="flex gap-4">
                        {ALL_CURRENT_TYPES.map(type => (
                            <div key={type} className="flex items-center space-x-2">
                                <Checkbox
                                    id={`filter-current-${type}`}
                                    checked={filters.currentTypes.includes(type)}
                                    onCheckedChange={() => toggleCurrentType(type)}
                                />
                                <Label htmlFor={`filter-current-${type}`} className="text-sm font-normal cursor-pointer">
                                    {type}
                                </Label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="border-t"></div>

                {/* POWER */}
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <Label className="text-base">Min Power (kW)</Label>
                        <span className="text-sm text-muted-foreground font-mono">
                            {filters.minPower.toFixed(1)} - {filters.maxPower.toFixed(1)} kW
                        </span>
                    </div>
                    <Slider
                        defaultValue={[0, MAX_POWER_LIMIT]}
                        value={[filters.minPower, filters.maxPower]}
                        min={0}
                        max={MAX_POWER_LIMIT}
                        step={0.1}
                        minStepsBetweenThumbs={1}
                        onValueChange={handlePowerChange}
                    />
                </div>

                <div className="border-t"></div>

                {/* PRICE */}
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <Label className="text-base">Price (CZK/kWh)</Label>
                        <span className="text-sm text-muted-foreground font-mono">
                            {filters.minPrice.toFixed(1)} - {filters.maxPrice.toFixed(1)} Kč
                        </span>
                    </div>
                    <Slider
                        defaultValue={[0, MAX_PRICE_LIMIT]}
                        value={[filters.minPrice, filters.maxPrice]}
                        min={0}
                        max={MAX_PRICE_LIMIT}
                        step={0.5}
                        minStepsBetweenThumbs={1}
                        onValueChange={handlePriceChange}
                    />
                </div>
            </div>

            <div className="p-4 border-t sticky bottom-0 bg-white">
                <Button variant="outline" className="w-full" onClick={onClear}>
                    Reset Filters
                </Button>
            </div>
        </div>
    );
}
