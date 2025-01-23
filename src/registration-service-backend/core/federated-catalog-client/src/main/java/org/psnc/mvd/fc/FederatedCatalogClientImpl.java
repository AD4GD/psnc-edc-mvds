
package org.psnc.mvd.fc;

import org.eclipse.edc.spi.response.StatusResult;
import org.psnc.mvd.fc.store.FederatedCatalogSqlStore;
import org.eclipse.edc.spi.monitor.Monitor;

public class FederatedCatalogClientImpl implements FederatedCatalogClient {

    private Monitor monitor;
    private FederatedCatalogSqlStore store;


    public FederatedCatalogClientImpl(Monitor monitor, FederatedCatalogSqlStore store) {
        this.monitor = monitor;
        this.store = store;
    }

    public StatusResult<Void> addParticipant(String did, String protocolUrl) {
        monitor.info("Added participant to Federated Catalog (FC): "+did+" "+protocolUrl);

        store.insertParticipant(did, protocolUrl);
        return StatusResult.success();
    }

    public StatusResult<Void> removeParticipant(String did) {
        monitor.info("Deleted participant from Federated Catalog (FC): "+did);

        store.deleteParticipant(did);
        return StatusResult.success();
    }
}
