
package org.psnc.mvd.fc;

import org.eclipse.edc.runtime.metamodel.annotation.ExtensionPoint;
import org.eclipse.edc.spi.response.StatusResult;

@ExtensionPoint
public interface FederatedCatalogClient {
    StatusResult<Void> addParticipant(String did, String protocolUrl);
    StatusResult<Void> removeParticipant(String did);
}
