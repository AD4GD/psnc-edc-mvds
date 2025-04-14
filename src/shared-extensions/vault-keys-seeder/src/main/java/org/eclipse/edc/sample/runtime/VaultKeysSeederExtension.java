
package org.eclipse.edc.sample.runtime;

import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.security.Vault;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.spi.monitor.Monitor;
import java.io.File;
import java.io.FileInputStream;
import java.security.Key;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.cert.Certificate;
import java.util.Base64;


public class VaultKeysSeederExtension implements ServiceExtension {

    public static final String NAME = "Vault Keys Seeder Service";

    private static final String DAPS_PRIVATE_KEY = "dapsPrivate";
    private static final String DAPS_CERTIFICATE_KEY = "dapsPublic";

    @Setting
    private static final String CONNECTOR_DAPS_KEYSTORE_FILE_PATH_NAME_SETTING = "psnc.connector.daps.keystore.file.path";

    @Setting
    private static final String CONNECTOR_DAPS_KEYSTORE_PASSWORD_NAME_SETTING = "psnc.connector.daps.keystore.password";

    @Setting
    private static final String CONNECTOR_CERTIFICATE_VALUE_NAME_SETTING = "psnc.connector.daps.certificate.value";

    @Setting
    private static final String CONNECTOR_PRIVATE_KEY_VALUE_NAME_SETTING = "psnc.connector.daps.private.key.value";

    @Inject
    private Vault vault;

    private Monitor monitor;

    @Override
    public void initialize(ServiceExtensionContext context) {

        monitor = context.getMonitor();

        var jksFilePath = context.getConfig().getString(CONNECTOR_DAPS_KEYSTORE_FILE_PATH_NAME_SETTING);
        var jksPassword = context.getConfig().getString(CONNECTOR_DAPS_KEYSTORE_PASSWORD_NAME_SETTING);
        processJksFile(jksFilePath, jksPassword);

        storeKeyIfSet(DAPS_PRIVATE_KEY, "PRIVATE KEY", context.getSetting(CONNECTOR_PRIVATE_KEY_VALUE_NAME_SETTING, null));
        storeKeyIfSet(DAPS_CERTIFICATE_KEY, "CERTIFICATE", context.getSetting(CONNECTOR_CERTIFICATE_VALUE_NAME_SETTING, null));
    }

    private void processJksFile(String keystorePath, String keystorePassword) {
        var alias = DAPS_PRIVATE_KEY;
        try {

            FileInputStream fis = new FileInputStream(keystorePath);
            KeyStore keystore = getKeyStore(keystorePath);
            keystore.load(fis, keystorePassword.toCharArray());

            Certificate cert = keystore.getCertificate(alias);
            if (cert != null) {
                String certBase64 = Base64.getEncoder().encodeToString(cert.getEncoded());
                storeKeyIfSet(DAPS_CERTIFICATE_KEY, "CERTIFICATE", certBase64);
            } else {
                monitor.info("Certificate not found for alias: " + alias);
            }

            Key key = keystore.getKey(alias, keystorePassword.toCharArray());
            if (key != null) {
                String keyBase64 = Base64.getEncoder().encodeToString(key.getEncoded());
                storeKeyIfSet(DAPS_PRIVATE_KEY, "PRIVATE KEY", keyBase64);
            } else {
                monitor.info("Private key not found for alias: " + alias);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private KeyStore getKeyStore(String keystorePath) throws KeyStoreException {
        String extension = "";

        int i = keystorePath.lastIndexOf('.');
        if (i > 0) {
            extension = keystorePath.substring(i+1).toLowerCase();
        }

        String keyStoreType = "";

        if (extension.equals("jks")) {
            keyStoreType = "JKS";
        }
        else if (extension.equals("pfx") || extension.equals("p12")) {
            keyStoreType = "PKCS12";
        }
        monitor.info("Key Store type: " + keyStoreType);

        return KeyStore.getInstance(keyStoreType);
    }

    private void storeKeyIfSet(String vaultKey, String keyType, String keyValue) {
        if (keyValue == null) {
            return;
        }

        var begin = String.format("BEGIN %s", keyType);
        var end = String.format("END %s", keyType);

        if (!keyValue.contains(begin)) {
            keyValue = String.format("""
                -----%s-----\n%s\n-----%s-----
                """, begin, keyValue, end);
        }

        monitor.info("Store: " + keyType);
        monitor.info(keyValue);

        vault.storeSecret(vaultKey, keyValue);
    }
}
