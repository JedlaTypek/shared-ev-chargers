/**
 * Převede výkon v kW na Watty (pro Solax nabíječky vyžadující Power)
 * @param {number} kw - Výkon v kW (např. 11)
 * @returns {number} - Výkon ve W (např. 11000)
 */
/**
 * Převede výkon v kW na Ampéry (pro 3 fáze, 230V)
 * Výpočet: (kw * 1000) / 3 / 230
 * @param {number} kw - Výkon v kW (např. 11)
 * @returns {number} - Proud v A (např. 16)
 */
export function kwToAmps(kw) {
  if (!kw) return 6; // Fallback safety minimum (6A)
  const watts = kw * 1000;
  return Math.round(watts / 3 / 230);
}

/**
 * Sestaví payload pro SetChargingProfile (v AMPERECH)
 * @param {number} connectorId 
 * @param {number} amps - Limit v Amperech
 * @param {string} purpose - 'TxDefaultProfile' nebo 'TxProfile'
 * @param {number|null} transactionId - Povinné pro TxProfile, jinak null
 */
export function buildChargingProfile(connectorId, amps, purpose, transactionId = null) {
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
      chargingRateUnit: "A", // <--- ZMĚNA: Posíláme 'A'
      chargingSchedulePeriod: [
        {
          startPeriod: 0,
          limit: amps, // <--- ZDE BUDE HODNOTA V AMPERECH (např. 16)
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