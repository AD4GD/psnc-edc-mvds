package org.gradle.accessors.dm;

import org.gradle.api.NonNullApi;
import org.gradle.api.artifacts.MinimalExternalModuleDependency;
import org.gradle.plugin.use.PluginDependency;
import org.gradle.api.artifacts.ExternalModuleDependencyBundle;
import org.gradle.api.artifacts.MutableVersionConstraint;
import org.gradle.api.provider.Provider;
import org.gradle.api.model.ObjectFactory;
import org.gradle.api.provider.ProviderFactory;
import org.gradle.api.internal.catalog.AbstractExternalDependencyFactory;
import org.gradle.api.internal.catalog.DefaultVersionCatalog;
import java.util.Map;
import org.gradle.api.internal.attributes.ImmutableAttributesFactory;
import org.gradle.api.internal.artifacts.dsl.CapabilityNotationParser;
import javax.inject.Inject;

/**
 * A catalog of dependencies accessible via the {@code libs} extension.
 */
@NonNullApi
public class LibrariesForLibsInPluginsBlock extends AbstractExternalDependencyFactory {

    private final AbstractExternalDependencyFactory owner = this;
    private final EdcLibraryAccessors laccForEdcLibraryAccessors = new EdcLibraryAccessors(owner);
    private final FlywayLibraryAccessors laccForFlywayLibraryAccessors = new FlywayLibraryAccessors(owner);
    private final JakartaLibraryAccessors laccForJakartaLibraryAccessors = new JakartaLibraryAccessors(owner);
    private final JettyLibraryAccessors laccForJettyLibraryAccessors = new JettyLibraryAccessors(owner);
    private final SovityLibraryAccessors laccForSovityLibraryAccessors = new SovityLibraryAccessors(owner);
    private final TractusLibraryAccessors laccForTractusLibraryAccessors = new TractusLibraryAccessors(owner);
    private final VersionAccessors vaccForVersionAccessors = new VersionAccessors(providers, config);
    private final BundleAccessors baccForBundleAccessors = new BundleAccessors(objects, providers, config, attributesFactory, capabilityNotationParser);
    private final PluginAccessors paccForPluginAccessors = new PluginAccessors(providers, config);

    @Inject
    public LibrariesForLibsInPluginsBlock(DefaultVersionCatalog config, ProviderFactory providers, ObjectFactory objects, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) {
        super(config, providers, objects, attributesFactory, capabilityNotationParser);
    }

    /**
     * Dependency provider for <b>lombok</b> with <b>org.projectlombok:lombok</b> coordinates and
     * with version reference <b>lombok</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public Provider<MinimalExternalModuleDependency> getLombok() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return create("lombok");
    }

    /**
     * Dependency provider for <b>postgresql</b> with <b>org.postgresql:postgresql</b> coordinates and
     * with version reference <b>postgres</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public Provider<MinimalExternalModuleDependency> getPostgresql() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return create("postgresql");
    }

    /**
     * Group of libraries at <b>edc</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public EdcLibraryAccessors getEdc() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForEdcLibraryAccessors;
    }

    /**
     * Group of libraries at <b>flyway</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public FlywayLibraryAccessors getFlyway() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForFlywayLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jakarta</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public JakartaLibraryAccessors getJakarta() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForJakartaLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jetty</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public JettyLibraryAccessors getJetty() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForJettyLibraryAccessors;
    }

    /**
     * Group of libraries at <b>sovity</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public SovityLibraryAccessors getSovity() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForSovityLibraryAccessors;
    }

    /**
     * Group of libraries at <b>tractus</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public TractusLibraryAccessors getTractus() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return laccForTractusLibraryAccessors;
    }

    /**
     * Group of versions at <b>versions</b>
     */
    public VersionAccessors getVersions() {
        return vaccForVersionAccessors;
    }

    /**
     * Group of bundles at <b>bundles</b>
     *
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public BundleAccessors getBundles() {
        org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
        return baccForBundleAccessors;
    }

    /**
     * Group of plugins at <b>plugins</b>
     */
    public PluginAccessors getPlugins() {
        return paccForPluginAccessors;
    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcLibraryAccessors extends SubDependencyFactory {
        private final EdcApiLibraryAccessors laccForEdcApiLibraryAccessors = new EdcApiLibraryAccessors(owner);
        private final EdcAuthLibraryAccessors laccForEdcAuthLibraryAccessors = new EdcAuthLibraryAccessors(owner);
        private final EdcBuildLibraryAccessors laccForEdcBuildLibraryAccessors = new EdcBuildLibraryAccessors(owner);
        private final EdcCallbackLibraryAccessors laccForEdcCallbackLibraryAccessors = new EdcCallbackLibraryAccessors(owner);
        private final EdcConfigurationLibraryAccessors laccForEdcConfigurationLibraryAccessors = new EdcConfigurationLibraryAccessors(owner);
        private final EdcConnectorLibraryAccessors laccForEdcConnectorLibraryAccessors = new EdcConnectorLibraryAccessors(owner);
        private final EdcControlLibraryAccessors laccForEdcControlLibraryAccessors = new EdcControlLibraryAccessors(owner);
        private final EdcCoreLibraryAccessors laccForEdcCoreLibraryAccessors = new EdcCoreLibraryAccessors(owner);
        private final EdcDataLibraryAccessors laccForEdcDataLibraryAccessors = new EdcDataLibraryAccessors(owner);
        private final EdcEdrLibraryAccessors laccForEdcEdrLibraryAccessors = new EdcEdrLibraryAccessors(owner);
        private final EdcFederatedLibraryAccessors laccForEdcFederatedLibraryAccessors = new EdcFederatedLibraryAccessors(owner);
        private final EdcIamLibraryAccessors laccForEdcIamLibraryAccessors = new EdcIamLibraryAccessors(owner);
        private final EdcJsonLibraryAccessors laccForEdcJsonLibraryAccessors = new EdcJsonLibraryAccessors(owner);
        private final EdcManagementLibraryAccessors laccForEdcManagementLibraryAccessors = new EdcManagementLibraryAccessors(owner);
        private final EdcMonitorLibraryAccessors laccForEdcMonitorLibraryAccessors = new EdcMonitorLibraryAccessors(owner);
        private final EdcOauth2LibraryAccessors laccForEdcOauth2LibraryAccessors = new EdcOauth2LibraryAccessors(owner);
        private final EdcSqlLibraryAccessors laccForEdcSqlLibraryAccessors = new EdcSqlLibraryAccessors(owner);
        private final EdcTransactionLibraryAccessors laccForEdcTransactionLibraryAccessors = new EdcTransactionLibraryAccessors(owner);
        private final EdcTransferLibraryAccessors laccForEdcTransferLibraryAccessors = new EdcTransferLibraryAccessors(owner);
        private final EdcValidatorLibraryAccessors laccForEdcValidatorLibraryAccessors = new EdcValidatorLibraryAccessors(owner);
        private final EdcVaultLibraryAccessors laccForEdcVaultLibraryAccessors = new EdcVaultLibraryAccessors(owner);

        public EdcLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>boot</b> with <b>org.eclipse.edc:boot</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getBoot() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.boot");
        }

        /**
         * Dependency provider for <b>dsp</b> with <b>org.eclipse.edc:dsp</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getDsp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.dsp");
        }

        /**
         * Dependency provider for <b>http</b> with <b>org.eclipse.edc:http</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getHttp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.http");
        }

        /**
         * Group of libraries at <b>edc.api</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcApiLibraryAccessors getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcApiLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.auth</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcAuthLibraryAccessors getAuth() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcAuthLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.build</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcBuildLibraryAccessors getBuild() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcBuildLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.callback</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcCallbackLibraryAccessors getCallback() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcCallbackLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.configuration</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcConfigurationLibraryAccessors getConfiguration() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcConfigurationLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.connector</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcConnectorLibraryAccessors getConnector() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcConnectorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.control</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcControlLibraryAccessors getControl() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.core</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcCoreLibraryAccessors getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcCoreLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataLibraryAccessors getData() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.edr</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcEdrLibraryAccessors getEdr() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcEdrLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.federated</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcFederatedLibraryAccessors getFederated() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcFederatedLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.iam</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcIamLibraryAccessors getIam() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcIamLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.json</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcJsonLibraryAccessors getJson() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcJsonLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.management</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcManagementLibraryAccessors getManagement() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcManagementLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.monitor</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcMonitorLibraryAccessors getMonitor() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcMonitorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.oauth2</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcOauth2LibraryAccessors getOauth2() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcOauth2LibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sql</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcSqlLibraryAccessors getSql() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcSqlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transaction</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransactionLibraryAccessors getTransaction() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransactionLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transfer</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransferLibraryAccessors getTransfer() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransferLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.validator</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcValidatorLibraryAccessors getValidator() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcValidatorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.vault</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcVaultLibraryAccessors getVault() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcVaultLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcApiLibraryAccessors extends SubDependencyFactory {

        public EdcApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>observability</b> with <b>org.eclipse.edc:api-observability</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getObservability() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.api.observability");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcAuthLibraryAccessors extends SubDependencyFactory {

        public EdcAuthLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>tokenbased</b> with <b>org.eclipse.edc:auth-tokenbased</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getTokenbased() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.auth.tokenbased");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcBuildLibraryAccessors extends SubDependencyFactory {

        public EdcBuildLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>plugin</b> with <b>org.eclipse.edc.edc-build:org.eclipse.edc.edc-build.gradle.plugin</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getPlugin() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.build.plugin");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcCallbackLibraryAccessors extends SubDependencyFactory {
        private final EdcCallbackEventLibraryAccessors laccForEdcCallbackEventLibraryAccessors = new EdcCallbackEventLibraryAccessors(owner);
        private final EdcCallbackHttpLibraryAccessors laccForEdcCallbackHttpLibraryAccessors = new EdcCallbackHttpLibraryAccessors(owner);

        public EdcCallbackLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.callback.event</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcCallbackEventLibraryAccessors getEvent() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcCallbackEventLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.callback.http</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcCallbackHttpLibraryAccessors getHttp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcCallbackHttpLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcCallbackEventLibraryAccessors extends SubDependencyFactory {

        public EdcCallbackEventLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dispatcher</b> with <b>org.eclipse.edc:callback-event-dispatcher</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getDispatcher() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.callback.event.dispatcher");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcCallbackHttpLibraryAccessors extends SubDependencyFactory {

        public EdcCallbackHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dispatcher</b> with <b>org.eclipse.edc:callback-http-dispatcher</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getDispatcher() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.callback.http.dispatcher");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcConfigurationLibraryAccessors extends SubDependencyFactory {

        public EdcConfigurationLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>filesystem</b> with <b>org.eclipse.edc:configuration-filesystem</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getFilesystem() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.configuration.filesystem");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcConnectorLibraryAccessors extends SubDependencyFactory {

        public EdcConnectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:connector-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.connector.core");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcControlLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneLibraryAccessors laccForEdcControlPlaneLibraryAccessors = new EdcControlPlaneLibraryAccessors(owner);

        public EdcControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.control.plane</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcControlPlaneLibraryAccessors getPlane() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcControlPlaneLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcControlPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneApiLibraryAccessors laccForEdcControlPlaneApiLibraryAccessors = new EdcControlPlaneApiLibraryAccessors(owner);

        public EdcControlPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:control-plane-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.control.plane.core");
        }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:control-plane-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSpi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.control.plane.spi");
        }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:control-plane-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSql() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.control.plane.sql");
        }

        /**
         * Group of libraries at <b>edc.control.plane.api</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcControlPlaneApiLibraryAccessors getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcControlPlaneApiLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcControlPlaneApiLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcControlPlaneApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:control-plane-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> asProvider() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.control.plane.api");
        }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:control-plane-api-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getClient() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.control.plane.api.client");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcCoreLibraryAccessors extends SubDependencyFactory {

        public EdcCoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:core-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSpi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.core.spi");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneLibraryAccessors laccForEdcDataPlaneLibraryAccessors = new EdcDataPlaneLibraryAccessors(owner);

        public EdcDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.data.plane</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneLibraryAccessors getPlane() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneControlLibraryAccessors laccForEdcDataPlaneControlLibraryAccessors = new EdcDataPlaneControlLibraryAccessors(owner);
        private final EdcDataPlaneInstanceLibraryAccessors laccForEdcDataPlaneInstanceLibraryAccessors = new EdcDataPlaneInstanceLibraryAccessors(owner);
        private final EdcDataPlanePublicLibraryAccessors laccForEdcDataPlanePublicLibraryAccessors = new EdcDataPlanePublicLibraryAccessors(owner);
        private final EdcDataPlaneSelectorLibraryAccessors laccForEdcDataPlaneSelectorLibraryAccessors = new EdcDataPlaneSelectorLibraryAccessors(owner);
        private final EdcDataPlaneSelfLibraryAccessors laccForEdcDataPlaneSelfLibraryAccessors = new EdcDataPlaneSelfLibraryAccessors(owner);

        public EdcDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:data-plane-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getClient() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.client");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:data-plane-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.core");
        }

        /**
         * Dependency provider for <b>http</b> with <b>org.eclipse.edc:data-plane-http</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getHttp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.http");
        }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:data-plane-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSpi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.spi");
        }

        /**
         * Dependency provider for <b>util</b> with <b>org.eclipse.edc:data-plane-util</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getUtil() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.util");
        }

        /**
         * Group of libraries at <b>edc.data.plane.control</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneControlLibraryAccessors getControl() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.instance</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneInstanceLibraryAccessors getInstance() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneInstanceLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.public</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlanePublicLibraryAccessors getPublic() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlanePublicLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.selector</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneSelectorLibraryAccessors getSelector() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneSelectorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.self</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneSelfLibraryAccessors getSelf() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneSelfLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneControlLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-control-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.control.api");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneInstanceLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneInstanceStoreLibraryAccessors laccForEdcDataPlaneInstanceStoreLibraryAccessors = new EdcDataPlaneInstanceStoreLibraryAccessors(owner);

        public EdcDataPlaneInstanceLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.data.plane.instance.store</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcDataPlaneInstanceStoreLibraryAccessors getStore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcDataPlaneInstanceStoreLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneInstanceStoreLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneInstanceStoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:data-plane-instance-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSql() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.instance.store.sql");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlanePublicLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlanePublicLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-public-api-v2</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.public.api");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneSelectorLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneSelectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-selector-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.selector.api");
        }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:data-plane-selector-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getClient() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.selector.client");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:data-plane-selector-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.selector.core");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcDataPlaneSelfLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneSelfLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>registration</b> with <b>org.eclipse.edc:data-plane-self-registration</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getRegistration() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.data.plane.self.registration");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcEdrLibraryAccessors extends SubDependencyFactory {
        private final EdcEdrCacheLibraryAccessors laccForEdcEdrCacheLibraryAccessors = new EdcEdrCacheLibraryAccessors(owner);
        private final EdcEdrStoreLibraryAccessors laccForEdcEdrStoreLibraryAccessors = new EdcEdrStoreLibraryAccessors(owner);

        public EdcEdrLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.edr.cache</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcEdrCacheLibraryAccessors getCache() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcEdrCacheLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.edr.store</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcEdrStoreLibraryAccessors getStore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcEdrStoreLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcEdrCacheLibraryAccessors extends SubDependencyFactory {

        public EdcEdrCacheLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:edr-cache-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.edr.cache.api");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcEdrStoreLibraryAccessors extends SubDependencyFactory {

        public EdcEdrStoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:edr-store-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.edr.store.core");
        }

        /**
         * Dependency provider for <b>receiver</b> with <b>org.eclipse.edc:edr-store-receiver</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getReceiver() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.edr.store.receiver");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcFederatedLibraryAccessors extends SubDependencyFactory {
        private final EdcFederatedCatalogLibraryAccessors laccForEdcFederatedCatalogLibraryAccessors = new EdcFederatedCatalogLibraryAccessors(owner);

        public EdcFederatedLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.federated.catalog</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcFederatedCatalogLibraryAccessors getCatalog() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcFederatedCatalogLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcFederatedCatalogLibraryAccessors extends SubDependencyFactory {

        public EdcFederatedCatalogLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:federated-catalog-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.federated.catalog.api");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:federated-catalog-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.federated.catalog.core");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcIamLibraryAccessors extends SubDependencyFactory {

        public EdcIamLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>mock</b> with <b>org.eclipse.edc:iam-mock</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getMock() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.iam.mock");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcJsonLibraryAccessors extends SubDependencyFactory {

        public EdcJsonLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>ld</b> with <b>org.eclipse.edc:json-ld</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getLd() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.json.ld");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcManagementLibraryAccessors extends SubDependencyFactory {

        public EdcManagementLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:management-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.management.api");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcMonitorLibraryAccessors extends SubDependencyFactory {
        private final EdcMonitorJdkLibraryAccessors laccForEdcMonitorJdkLibraryAccessors = new EdcMonitorJdkLibraryAccessors(owner);

        public EdcMonitorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.monitor.jdk</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcMonitorJdkLibraryAccessors getJdk() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcMonitorJdkLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcMonitorJdkLibraryAccessors extends SubDependencyFactory {

        public EdcMonitorJdkLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>logger</b> with <b>org.eclipse.edc:monitor-jdk-logger</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getLogger() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.monitor.jdk.logger");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcOauth2LibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcOauth2LibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>oauth2</b> with <b>org.eclipse.edc:oauth2-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> asProvider() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.oauth2");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:oauth2-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.oauth2.core");
        }

        /**
         * Dependency provider for <b>daps</b> with <b>org.eclipse.edc:oauth2-daps</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getDaps() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.oauth2.daps");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcSqlLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolLibraryAccessors laccForEdcSqlPoolLibraryAccessors = new EdcSqlPoolLibraryAccessors(owner);

        public EdcSqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:sql-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.sql.core");
        }

        /**
         * Group of libraries at <b>edc.sql.pool</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcSqlPoolLibraryAccessors getPool() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcSqlPoolLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcSqlPoolLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolApacheLibraryAccessors laccForEdcSqlPoolApacheLibraryAccessors = new EdcSqlPoolApacheLibraryAccessors(owner);

        public EdcSqlPoolLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.sql.pool.apache</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcSqlPoolApacheLibraryAccessors getApache() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcSqlPoolApacheLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcSqlPoolApacheLibraryAccessors extends SubDependencyFactory {

        public EdcSqlPoolApacheLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>commons</b> with <b>org.eclipse.edc:sql-pool-apache-commons</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCommons() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.sql.pool.apache.commons");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransactionLibraryAccessors extends SubDependencyFactory {

        public EdcTransactionLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>local</b> with <b>org.eclipse.edc:transaction-local</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getLocal() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.transaction.local");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransferLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferDataLibraryAccessors laccForEdcTransferDataLibraryAccessors = new EdcTransferDataLibraryAccessors(owner);
        private final EdcTransferPullLibraryAccessors laccForEdcTransferPullLibraryAccessors = new EdcTransferPullLibraryAccessors(owner);

        public EdcTransferLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:transfer-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSpi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.transfer.spi");
        }

        /**
         * Group of libraries at <b>edc.transfer.data</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransferDataLibraryAccessors getData() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransferDataLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transfer.pull</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransferPullLibraryAccessors getPull() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransferPullLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransferDataLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferDataPlaneLibraryAccessors laccForEdcTransferDataPlaneLibraryAccessors = new EdcTransferDataPlaneLibraryAccessors(owner);

        public EdcTransferDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.transfer.data.plane</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransferDataPlaneLibraryAccessors getPlane() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransferDataPlaneLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransferDataPlaneLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcTransferDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>plane</b> with <b>org.eclipse.edc:transfer-data-plane</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> asProvider() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.transfer.data.plane");
        }

        /**
         * Dependency provider for <b>signaling</b> with <b>org.eclipse.edc:transfer-data-plane-signaling</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getSignaling() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.transfer.data.plane.signaling");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransferPullLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferPullHttpLibraryAccessors laccForEdcTransferPullHttpLibraryAccessors = new EdcTransferPullHttpLibraryAccessors(owner);

        public EdcTransferPullLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.transfer.pull.http</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcTransferPullHttpLibraryAccessors getHttp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcTransferPullHttpLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcTransferPullHttpLibraryAccessors extends SubDependencyFactory {

        public EdcTransferPullHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>receiver</b> with <b>org.eclipse.edc:transfer-pull-http-receiver</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getReceiver() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.transfer.pull.http.receiver");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcValidatorLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataLibraryAccessors laccForEdcValidatorDataLibraryAccessors = new EdcValidatorDataLibraryAccessors(owner);

        public EdcValidatorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcValidatorDataLibraryAccessors getData() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcValidatorDataLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcValidatorDataLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataAddressLibraryAccessors laccForEdcValidatorDataAddressLibraryAccessors = new EdcValidatorDataAddressLibraryAccessors(owner);

        public EdcValidatorDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data.address</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcValidatorDataAddressLibraryAccessors getAddress() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcValidatorDataAddressLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcValidatorDataAddressLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataAddressHttpLibraryAccessors laccForEdcValidatorDataAddressHttpLibraryAccessors = new EdcValidatorDataAddressHttpLibraryAccessors(owner);

        public EdcValidatorDataAddressLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data.address.http</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public EdcValidatorDataAddressHttpLibraryAccessors getHttp() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForEdcValidatorDataAddressHttpLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcValidatorDataAddressHttpLibraryAccessors extends SubDependencyFactory {

        public EdcValidatorDataAddressHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>data</b> with <b>org.eclipse.edc:validator-data-address-http-data</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getData() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.validator.data.address.http.data");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class EdcVaultLibraryAccessors extends SubDependencyFactory {

        public EdcVaultLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>filesystem</b> with <b>org.eclipse.edc:vault-filesystem</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getFilesystem() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("edc.vault.filesystem");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class FlywayLibraryAccessors extends SubDependencyFactory {

        public FlywayLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.flywaydb:flyway-core</b> coordinates and
         * with version reference <b>flyway</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getCore() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("flyway.core");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class JakartaLibraryAccessors extends SubDependencyFactory {

        public JakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>rsApi</b> with <b>jakarta.ws.rs:jakarta.ws.rs-api</b> coordinates and
         * with version reference <b>rsApi</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getRsApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("jakarta.rsApi");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class JettyLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaLibraryAccessors laccForJettyJakartaLibraryAccessors = new JettyJakartaLibraryAccessors(owner);

        public JettyLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jetty.jakarta</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public JettyJakartaLibraryAccessors getJakarta() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForJettyJakartaLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class JettyJakartaLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaServletLibraryAccessors laccForJettyJakartaServletLibraryAccessors = new JettyJakartaServletLibraryAccessors(owner);

        public JettyJakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jetty.jakarta.servlet</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public JettyJakartaServletLibraryAccessors getServlet() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForJettyJakartaServletLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class JettyJakartaServletLibraryAccessors extends SubDependencyFactory {

        public JettyJakartaServletLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.jetty.toolchain:jetty-jakarta-servlet-api</b> coordinates and
         * with version reference <b>jetty.jakarta.servlet.api</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getApi() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("jetty.jakarta.servlet.api");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class SovityLibraryAccessors extends SubDependencyFactory {

        public SovityLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>pgflyway</b> with <b>de.sovity.edc.ext:postgres-flyway</b> coordinates and
         * with version reference <b>sovityext</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getPgflyway() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("sovity.pgflyway");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlLibraryAccessors laccForTractusPostgresqlLibraryAccessors = new TractusPostgresqlLibraryAccessors(owner);

        public TractusLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public TractusPostgresqlLibraryAccessors getPostgresql() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForTractusPostgresqlLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusPostgresqlLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlControlLibraryAccessors laccForTractusPostgresqlControlLibraryAccessors = new TractusPostgresqlControlLibraryAccessors(owner);
        private final TractusPostgresqlDataLibraryAccessors laccForTractusPostgresqlDataLibraryAccessors = new TractusPostgresqlDataLibraryAccessors(owner);

        public TractusPostgresqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.control</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public TractusPostgresqlControlLibraryAccessors getControl() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForTractusPostgresqlControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>tractus.postgresql.data</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public TractusPostgresqlDataLibraryAccessors getData() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForTractusPostgresqlDataLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusPostgresqlControlLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlControlPlaneLibraryAccessors laccForTractusPostgresqlControlPlaneLibraryAccessors = new TractusPostgresqlControlPlaneLibraryAccessors(owner);

        public TractusPostgresqlControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.control.plane</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public TractusPostgresqlControlPlaneLibraryAccessors getPlane() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForTractusPostgresqlControlPlaneLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusPostgresqlControlPlaneLibraryAccessors extends SubDependencyFactory {

        public TractusPostgresqlControlPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>migration</b> with <b>org.eclipse.tractusx.edc:control-plane-migration</b> coordinates and
         * with version reference <b>tractus</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getMigration() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("tractus.postgresql.control.plane.migration");
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusPostgresqlDataLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlDataPlaneLibraryAccessors laccForTractusPostgresqlDataPlaneLibraryAccessors = new TractusPostgresqlDataPlaneLibraryAccessors(owner);

        public TractusPostgresqlDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.data.plane</b>
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public TractusPostgresqlDataPlaneLibraryAccessors getPlane() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return laccForTractusPostgresqlDataPlaneLibraryAccessors;
        }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class TractusPostgresqlDataPlaneLibraryAccessors extends SubDependencyFactory {

        public TractusPostgresqlDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>migration</b> with <b>org.eclipse.tractusx.edc:data-plane-migration</b> coordinates and
         * with version reference <b>tractus</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         *
         * @deprecated Will be removed in Gradle 9.0.
         */
        @Deprecated
        public Provider<MinimalExternalModuleDependency> getMigration() {
            org.gradle.internal.deprecation.DeprecationLogger.deprecateBehaviour("Accessing libraries or bundles from version catalogs in the plugins block.").withAdvice("Only use versions or plugins from catalogs in the plugins block.").willBeRemovedInGradle9().withUpgradeGuideSection(8, "kotlin_dsl_deprecated_catalogs_plugins_block").nagUser();
            return create("tractus.postgresql.data.plane.migration");
        }

    }

    public static class VersionAccessors extends VersionFactory  {

        private final JakartaVersionAccessors vaccForJakartaVersionAccessors = new JakartaVersionAccessors(providers, config);
        private final JettyVersionAccessors vaccForJettyVersionAccessors = new JettyVersionAccessors(providers, config);
        private final JunitVersionAccessors vaccForJunitVersionAccessors = new JunitVersionAccessors(providers, config);
        private final OkhttpVersionAccessors vaccForOkhttpVersionAccessors = new OkhttpVersionAccessors(providers, config);
        public VersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>assertj</b> with value <b>3.24.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getAssertj() { return getVersion("assertj"); }

        /**
         * Version alias <b>awaitility</b> with value <b>4.2.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getAwaitility() { return getVersion("awaitility"); }

        /**
         * Version alias <b>edc</b> with value <b>0.7.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getEdc() { return getVersion("edc"); }

        /**
         * Version alias <b>flyway</b> with value <b>9.0.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getFlyway() { return getVersion("flyway"); }

        /**
         * Version alias <b>jupiter</b> with value <b>5.10.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJupiter() { return getVersion("jupiter"); }

        /**
         * Version alias <b>kafkaClients</b> with value <b>3.6.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getKafkaClients() { return getVersion("kafkaClients"); }

        /**
         * Version alias <b>lombok</b> with value <b>1.18.28</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getLombok() { return getVersion("lombok"); }

        /**
         * Version alias <b>openTelemetry</b> with value <b>1.18.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getOpenTelemetry() { return getVersion("openTelemetry"); }

        /**
         * Version alias <b>postgres</b> with value <b>42.4.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getPostgres() { return getVersion("postgres"); }

        /**
         * Version alias <b>restAssured</b> with value <b>5.3.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getRestAssured() { return getVersion("restAssured"); }

        /**
         * Version alias <b>rsApi</b> with value <b>3.1.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getRsApi() { return getVersion("rsApi"); }

        /**
         * Version alias <b>sovityext</b> with value <b>4.2.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getSovityext() { return getVersion("sovityext"); }

        /**
         * Version alias <b>testcontainers</b> with value <b>1.19.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getTestcontainers() { return getVersion("testcontainers"); }

        /**
         * Version alias <b>tractus</b> with value <b>0.7.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getTractus() { return getVersion("tractus"); }

        /**
         * Group of versions at <b>versions.jakarta</b>
         */
        public JakartaVersionAccessors getJakarta() {
            return vaccForJakartaVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.jetty</b>
         */
        public JettyVersionAccessors getJetty() {
            return vaccForJettyVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.junit</b>
         */
        public JunitVersionAccessors getJunit() {
            return vaccForJunitVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.okhttp</b>
         */
        public OkhttpVersionAccessors getOkhttp() {
            return vaccForOkhttpVersionAccessors;
        }

    }

    public static class JakartaVersionAccessors extends VersionFactory  {

        public JakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>jakarta.json</b> with value <b>2.0.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJson() { return getVersion("jakarta.json"); }

    }

    public static class JettyVersionAccessors extends VersionFactory  {

        private final JettyJakartaVersionAccessors vaccForJettyJakartaVersionAccessors = new JettyJakartaVersionAccessors(providers, config);
        public JettyVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Group of versions at <b>versions.jetty.jakarta</b>
         */
        public JettyJakartaVersionAccessors getJakarta() {
            return vaccForJettyJakartaVersionAccessors;
        }

    }

    public static class JettyJakartaVersionAccessors extends VersionFactory  {

        private final JettyJakartaServletVersionAccessors vaccForJettyJakartaServletVersionAccessors = new JettyJakartaServletVersionAccessors(providers, config);
        public JettyJakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Group of versions at <b>versions.jetty.jakarta.servlet</b>
         */
        public JettyJakartaServletVersionAccessors getServlet() {
            return vaccForJettyJakartaServletVersionAccessors;
        }

    }

    public static class JettyJakartaServletVersionAccessors extends VersionFactory  {

        public JettyJakartaServletVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>jetty.jakarta.servlet.api</b> with value <b>5.0.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getApi() { return getVersion("jetty.jakarta.servlet.api"); }

    }

    public static class JunitVersionAccessors extends VersionFactory  {

        public JunitVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>junit.pioneer</b> with value <b>2.1.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getPioneer() { return getVersion("junit.pioneer"); }

    }

    public static class OkhttpVersionAccessors extends VersionFactory  {

        public OkhttpVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>okhttp.mockwebserver</b> with value <b>5.0.0-alpha.11</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getMockwebserver() { return getVersion("okhttp.mockwebserver"); }

    }

    /**
     * @deprecated Will be removed in Gradle 9.0.
     */
    @Deprecated
    public static class BundleAccessors extends BundleFactory {

        public BundleAccessors(ObjectFactory objects, ProviderFactory providers, DefaultVersionCatalog config, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) { super(objects, providers, config, attributesFactory, capabilityNotationParser); }

    }

    public static class PluginAccessors extends PluginFactory {

        public PluginAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Plugin provider for <b>shadow</b> with plugin id <b>com.github.johnrengelman.shadow</b> and
         * with version <b>8.1.1</b>
         * <p>
         * This plugin was declared in catalog libs.versions.toml
         */
        public Provider<PluginDependency> getShadow() { return createPlugin("shadow"); }

    }

}
