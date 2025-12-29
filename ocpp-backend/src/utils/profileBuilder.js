/**
 * Převede výkon v kW na Watty (pro Solax nabíječky vyžadující Power)
 * @param {number} kw - Výkon v kW (např. 11)
 * @returns {number} - Výkon ve W (např. 11000)
 */
export function kwToWatts(kw) {
  if (!kw) return 4000; // Fallback safety minimum (cca 6A)
  return Math.floor(kw * 1000); 
}

/**
 * Sestaví payload pro SetChargingProfile (ve WATTECH)
 * @param {number} connectorId 
 * @param {number} watts - Limit ve Wattech
 * @param {string} purpose - 'TxDefaultProfile' nebo 'TxProfile'
 * @param {number|null} transactionId - Povinné pro TxProfile, jinak null
 */
export function buildChargingProfile(connectorId, watts, purpose, transactionId = null) {
  const isTxProfile = purpose === 'TxProfile';
  const now = new Date();
  now.setMinutes(now.getMinutes() - 10); 

  const csChargingProfiles = {
      chargingProfileId: isTxProfile ? 100 : 1,
      stackLevel: isTxProfile ? 1 : 0,
      chargingProfilePurpose: purpose,
      chargingProfileKind: isTxProfile ? "Absolute" : "Recurring", 
      chargingSchedule: {
        duration: 86400,
        startSchedule: now.toISOString(),
        chargingRateUnit: "W", // <--- ZMĚNA: Tady musíme poslat 'W' (nebo 'Power' u starších verzí, ale OCPP říká 'W')
        chargingSchedulePeriod: [
          {
            startPeriod: 0,
            limit: watts, // <--- ZDE BUDE HODNOTA VE WATTECH (např. 11000)
            numberPhases: 3
          }
        ]
      }
  };

  if (transactionId) {
      csChargingProfiles.transactionId = transactionId;
  }

  if (!isTxProfile) {
      csChargingProfiles.recurrencyKind = "Daily";
  }

  return {
    connectorId: connectorId,
    csChargingProfiles: csChargingProfiles
  };
}