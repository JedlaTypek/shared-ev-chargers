import apiClient from "../utils/apiClient.js";

export const handleHeartbeat = async ({ client }) => {
  const { chargePointId } = client;

  try {
    // 1. Pošleme notifikaci na backend (aby si uložil, že nabíječka žije)
    const response = await apiClient.post(`/heartbeat/${chargePointId}`);

    // 2. Získáme čas.
    // Backend vrátí např.: "2023-12-20T12:00:00+00:00"
    // My to raději převedeme na: "2023-12-20T12:00:00.000Z" (což mají nabíječky raději)
    let currentTime;
    
    if (response.data && response.data.currentTime) {
      currentTime = new Date(response.data.currentTime).toISOString();
    } else {
      currentTime = new Date().toISOString();
    }

    return {
      currentTime: currentTime
    };

  } catch (error) {
    // Pokud API selže, logujeme chybu, ale nabíječce odpovíme lokálním časem,
    // aby si nemyslela, že je chyba v ní.
    console.error(`Heartbeat failed for ${chargePointId}:`, error.message);
    
    return {
      currentTime: new Date().toISOString()
    };
  }
};