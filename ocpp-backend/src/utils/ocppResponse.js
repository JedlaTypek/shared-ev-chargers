/**
 * Pomocné funkce pro generování standardních OCPP 1.6 odpovědí.
 * Tyto funkce vrací čisté JSON objekty (payload), které ocpp-rpc zabalí do CallResult.
 */

// Pomocná funkce pro aktuální čas v ISO formátu (UTC)
const now = () => new Date().toISOString();

export const ocppResponse = {
  /**
   * Odpověď na BootNotification
   * @param {string} status - "Accepted", "Pending", "Rejected"
   * @param {number} interval - Heartbeat interval v sekundách
   */
  bootNotification: (status, interval) => {
    return {
      status,
      currentTime: now(),
      interval,
    };
  },

  /**
   * Odpověď na Heartbeat
   */
  heartbeat: () => {
    return {
      currentTime: now(),
    };
  },

  /**
   * Odpověď na StatusNotification
   * (StatusNotificationResponse je prázdný objekt)
   */
  statusNotification: () => {
    return {};
  },

  /**
   * Odpověď na Authorize
   * @param {string} status - "Accepted", "Blocked", "Expired", "Invalid", "ConcurrentTx"
   * @param {string} [parentIdTag] - Volitelné, pro skupiny
   * @param {string} [expiryDate] - Volitelné, kdy expiruje karta
   */
  authorize: (status, parentIdTag = null, expiryDate = null) => {
    const idTagInfo = { status };
    if (parentIdTag) idTagInfo.parentIdTag = parentIdTag;
    if (expiryDate) idTagInfo.expiryDate = expiryDate;

    return { idTagInfo };
  },

  /**
   * Odpověď na StartTransaction
   * @param {number} transactionId - ID transakce vygenerované backendem
   * @param {string} status - Stav autorizace ("Accepted", "Blocked", atd.)
   */
  startTransaction: (transactionId, status = "Accepted") => {
    return {
      transactionId,
      idTagInfo: {
        status,
      },
    };
  },

  /**
   * Odpověď na StopTransaction
   * @param {string} [status] - Volitelný stav idTagu ("Accepted", "Expired"...)
   */
  stopTransaction: (status = null) => {
    // StopTransactionResponse může obsahovat idTagInfo, pokud chceme kartu po ukončení invalidovat
    if (status) {
      return {
        idTagInfo: {
          status,
        },
      };
    }
    return {};
  },

  /**
   * Odpověď na MeterValues
   * (MeterValuesResponse je prázdný objekt)
   */
  meterValues: () => {
    return {};
  },
  
  /**
   * Odpověď na FirmwareStatusNotification
   * (FirmwareStatusNotificationResponse je prázdný objekt)
   */
  firmwareStatusNotification: () => {
    return {};
  },

  /**
   * Odpověď na DiagnosticsStatusNotification
   * (DiagnosticsStatusNotificationResponse je prázdný objekt)
   */
  diagnosticsStatusNotification: () => {
    return {};
  },
  
  /**
   * Generická odpověď úspěchu (pro prázdné odpovědi)
   */
  success: () => {
    return {};
  }
};