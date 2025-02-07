
package org.eclipse.edc.sample.runtime;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.eclipse.edc.api.auth.spi.AuthenticationService;
import org.eclipse.edc.spi.monitor.Monitor;

public class NoneAuthenticationService implements AuthenticationService {

    private final Monitor monitor;


    public NoneAuthenticationService(Monitor monitor) {
        this.monitor = monitor;
    }

    @Override
    public boolean isAuthenticated(Map<String, List<String>> headers) {
        return true;
    }
}
