package com.psnc.mvds.ishare.extension;

import com.psnc.mvds.ishare.client.IShareParticipantRegistryClient;
import com.psnc.mvds.ishare.service.IShareTokenService;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.web.spi.WebService;

/**
 * Extension that registers the iShare API controller with EDC's web service
 */
@Extension(value = IShareParticipantRegistryApiExtension.NAME)
public class IShareParticipantRegistryApiExtension implements ServiceExtension {
    
    public static final String NAME = "iShare Participant Registry API Extension";
    
    @Inject
    private WebService webService;
    
    @Inject
    private IShareTokenService tokenService;
    
    @Inject
    private IShareParticipantRegistryClient prClient;
    
    @Override
    public String name() {
        return NAME;
    }
    
    @Override
    public void initialize(ServiceExtensionContext context) {
        if (tokenService != null && prClient != null) {
            var controller = new IShareParticipantRegistryApiController(tokenService, prClient);
            webService.registerResource(controller);
            context.getMonitor().info("iShare Participant Registry API registered at /api/ishare/*");
        } else {
            context.getMonitor().warning("iShare Participant Registry services not available, API not registered");
        }
    }
}
