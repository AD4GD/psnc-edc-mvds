
package org.psnc.mvd.identity;

import java.util.Map;

import org.eclipse.edc.runtime.metamodel.annotation.ExtensionPoint;
import org.eclipse.edc.spi.response.StatusResult;
import org.psnc.mvd.identity.models.IdentityClientModel;

@ExtensionPoint
public interface IdentityProviderClient {
    StatusResult<IdentityClientModel> getClient(String clientId);
    StatusResult<Void> addClient(String clientId);
    StatusResult<Void> updateClient(String clientId, Map<String, String> claims);
    StatusResult<Void> deleteClient(String clientId);
}