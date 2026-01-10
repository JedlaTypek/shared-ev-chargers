import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

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

interface LocationPickerProps {
    latitude?: number;
    longitude?: number;
    onLocationSelect: (lat: number, lng: number) => void;
}

function LocationMarker({ position, onLocationSelect }: { position: [number, number] | null, onLocationSelect: (lat: number, lng: number) => void }) {
    const map = useMapEvents({
        click(e) {
            onLocationSelect(e.latlng.lat, e.latlng.lng);
        },
    });

    useEffect(() => {
        if (position) {
            map.flyTo(position, map.getZoom());
        }
    }, [position, map]);

    return position === null ? null : (
        <Marker position={position}></Marker>
    );
}

export default function LocationPicker({ latitude, longitude, onLocationSelect }: LocationPickerProps) {
    // Default center (Prague) if no location selected yet
    const defaultCenter: [number, number] = [50.0755, 14.4378];
    const center = latitude && longitude ? [latitude, longitude] as [number, number] : defaultCenter;
    const position = latitude && longitude ? [latitude, longitude] as [number, number] : null;

    return (
        <div className="h-[300px] w-full rounded-md overflow-hidden border">
            <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationMarker position={position} onLocationSelect={onLocationSelect} />
            </MapContainer>
        </div>
    );
}
