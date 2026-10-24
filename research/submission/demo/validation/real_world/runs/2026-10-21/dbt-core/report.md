repo: dbt-core
docs=108 claims=3909 referents=1381 evidence=7679
code_verdicts: {'REFUTED': 455, 'SUPPORTED': 256, 'NEI': 733}  coverage=0.49  resolved=711

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 40 items in 13 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 1
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    HAS_DOCKERFILE   SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 3
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      SYSTEMATIC      neg=0: 3
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=1: 1
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    SYSTEMATIC      neg=0: 1
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=1: 4
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 455 of 455):
  1. PATH_EXISTS agents.local.md AGENTS.md:47-47
     tier: bare
     raw: Respect author preferences (optional/local): `AGENTS.local.md`
     cited by 2 claims
  2. PATH_EXISTS manifest.json README.md:24-24
     tier: bare
     raw: `manifest.json`), which continue to be produced for backwards compatibility.
     cited by 4 claims
  3. DEPENDENCY python crates/dbt-adapter/tests/snowflake_context_deadline_exceeded_repro_project/README.md:49-49
     tier: -
     raw: ### Why Python is ~2 min
     evidence: python:crates/dbt-sa-python/pyproject.toml:>=3.10, python:pyproject.toml:>=3.9
  4. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsapi.md crates/dbt-cloud-api/README.md:101-101
     tier: anchored
     raw: Method [**list_credentials**](docs/CredentialsApi.md#list_credentials)
  5. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectioncreatebodyrequest.md crates/dbt-cloud-api/README.md:105-105
     tier: anchored
     raw: [AccountConnectionCreateBodyRequest](docs/AccountConnectionCreateBodyRequest.md)
  6. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectiondetail.md crates/dbt-cloud-api/README.md:106-106
     tier: anchored
     raw: [AccountConnectionDetail](docs/AccountConnectionDetail.md)
  7. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectiondetailresponse.md crates/dbt-cloud-api/README.md:107-107
     tier: anchored
     raw: [AccountConnectionDetailResponse](docs/AccountConnectionDetailResponse.md)
  8. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectionlist.md crates/dbt-cloud-api/README.md:108-108
     tier: anchored
     raw: [AccountConnectionList](docs/AccountConnectionList.md)
  9. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectionlistresponse.md crates/dbt-cloud-api/README.md:109-109
     tier: anchored
     raw: [AccountConnectionListResponse](docs/AccountConnectionListResponse.md)
  10. PATH_EXISTS crates/dbt-cloud-api/docs/accountconnectionupdatebodyrequest.md crates/dbt-cloud-api/README.md:110-110
     tier: anchored
     raw: [AccountConnectionUpdateBodyRequest](docs/AccountConnectionUpdateBodyRequest.md)
  11. PATH_EXISTS crates/dbt-cloud-api/docs/accountlistenveloped.md crates/dbt-cloud-api/README.md:111-111
     tier: anchored
     raw: [AccountListEnveloped](docs/AccountListEnveloped.md)
  12. PATH_EXISTS crates/dbt-cloud-api/docs/accountresponse.md crates/dbt-cloud-api/README.md:112-112
     tier: anchored
     raw: [AccountResponse](docs/AccountResponse.md)
  13. PATH_EXISTS crates/dbt-cloud-api/docs/accountscopedpatrequestrequest.md crates/dbt-cloud-api/README.md:113-113
     tier: anchored
     raw: [AccountScopedPatRequestRequest](docs/AccountScopedPatRequestRequest.md)
  14. PATH_EXISTS crates/dbt-cloud-api/docs/accountscopedpatresponse.md crates/dbt-cloud-api/README.md:114-114
     tier: anchored
     raw: [AccountScopedPatResponse](docs/AccountScopedPatResponse.md)
  15. PATH_EXISTS crates/dbt-cloud-api/docs/accountscopedpatresponseenveloped.md crates/dbt-cloud-api/README.md:115-115
     tier: anchored
     raw: [AccountScopedPatResponseEnveloped](docs/AccountScopedPatResponseEnveloped.md)
  16. PATH_EXISTS crates/dbt-cloud-api/docs/accountuser.md crates/dbt-cloud-api/README.md:116-116
     tier: anchored
     raw: [AccountUser](docs/AccountUser.md)
  17. PATH_EXISTS crates/dbt-cloud-api/docs/accountuserlicense.md crates/dbt-cloud-api/README.md:117-117
     tier: anchored
     raw: [AccountUserLicense](docs/AccountUserLicense.md)
  18. PATH_EXISTS crates/dbt-cloud-api/docs/adapter.md crates/dbt-cloud-api/README.md:118-118
     tier: anchored
     raw: [Adapter](docs/Adapter.md)
  19. PATH_EXISTS crates/dbt-cloud-api/docs/adaptermetadata.md crates/dbt-cloud-api/README.md:119-119
     tier: anchored
     raw: [AdapterMetadata](docs/AdapterMetadata.md)
  20. PATH_EXISTS crates/dbt-cloud-api/docs/adapterschemaresponse.md crates/dbt-cloud-api/README.md:120-120
     tier: anchored
     raw: [AdapterSchemaResponse](docs/AdapterSchemaResponse.md)
  21. PATH_EXISTS crates/dbt-cloud-api/docs/adapterschemaresponseenveloped.md crates/dbt-cloud-api/README.md:121-121
     tier: anchored
     raw: [AdapterSchemaResponseEnveloped](docs/AdapterSchemaResponseEnveloped.md)
  22. PATH_EXISTS crates/dbt-cloud-api/docs/adapterversionenum.md crates/dbt-cloud-api/README.md:122-122
     tier: anchored
     raw: [AdapterVersionEnum](docs/AdapterVersionEnum.md)
  23. PATH_EXISTS crates/dbt-cloud-api/docs/apachesparkconnection.md crates/dbt-cloud-api/README.md:123-123
     tier: anchored
     raw: [ApacheSparkConnection](docs/ApacheSparkConnection.md)
  24. PATH_EXISTS crates/dbt-cloud-api/docs/assigngroupsrequestrequest.md crates/dbt-cloud-api/README.md:124-124
     tier: anchored
     raw: [AssignGroupsRequestRequest](docs/AssignGroupsRequestRequest.md)
  25. PATH_EXISTS crates/dbt-cloud-api/docs/athenaconnection.md crates/dbt-cloud-api/README.md:125-125
     tier: anchored
     raw: [AthenaConnection](docs/AthenaConnection.md)
  26. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogbulkexportdownloadresponse.md crates/dbt-cloud-api/README.md:126-126
     tier: anchored
     raw: [AuditLogBulkExportDownloadResponse](docs/AuditLogBulkExportDownloadResponse.md)
  27. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogbulkexportdownloadresponseenveloped.md crates/dbt-cloud-api/README.md:127-127
     tier: anchored
     raw: [AuditLogBulkExportDownloadResponseEnveloped](docs/AuditLogBulkExportDownloadResponseEnveloped.md)
  28. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogbulkexportstatusresponse.md crates/dbt-cloud-api/README.md:128-128
     tier: anchored
     raw: [AuditLogBulkExportStatusResponse](docs/AuditLogBulkExportStatusResponse.md)
  29. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogbulkexportstatusresponseenveloped.md crates/dbt-cloud-api/README.md:129-129
     tier: anchored
     raw: [AuditLogBulkExportStatusResponseEnveloped](docs/AuditLogBulkExportStatusResponseEnveloped.md)
  30. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogstartbulkexportresponse.md crates/dbt-cloud-api/README.md:130-130
     tier: anchored
     raw: [AuditLogStartBulkExportResponse](docs/AuditLogStartBulkExportResponse.md)
  31. PATH_EXISTS crates/dbt-cloud-api/docs/auditlogstartbulkexportresponseenveloped.md crates/dbt-cloud-api/README.md:131-131
     tier: anchored
     raw: [AuditLogStartBulkExportResponseEnveloped](docs/AuditLogStartBulkExportResponseEnveloped.md)
  32. PATH_EXISTS crates/dbt-cloud-api/docs/baseconnectionv3.md crates/dbt-cloud-api/README.md:132-132
     tier: anchored
     raw: [BaseConnectionV3](docs/BaseConnectionV3.md)
  33. PATH_EXISTS crates/dbt-cloud-api/docs/baseconnectionv3enveloped.md crates/dbt-cloud-api/README.md:133-133
     tier: anchored
     raw: [BaseConnectionV3Enveloped](docs/BaseConnectionV3Enveloped.md)
  34. PATH_EXISTS crates/dbt-cloud-api/docs/baseconnectionv3listenveloped.md crates/dbt-cloud-api/README.md:134-134
     tier: anchored
     raw: [BaseConnectionV3ListEnveloped](docs/BaseConnectionV3ListEnveloped.md)
  35. PATH_EXISTS crates/dbt-cloud-api/docs/baseconnectionv3request.md crates/dbt-cloud-api/README.md:135-135
     tier: anchored
     raw: [BaseConnectionV3Request](docs/BaseConnectionV3Request.md)
  36. PATH_EXISTS crates/dbt-cloud-api/docs/baseconnectionv3response.md crates/dbt-cloud-api/README.md:136-136
     tier: anchored
     raw: [BaseConnectionV3Response](docs/BaseConnectionV3Response.md)
  37. PATH_EXISTS crates/dbt-cloud-api/docs/basesparkadaptercredentialfields.md crates/dbt-cloud-api/README.md:137-137
     tier: anchored
     raw: [BaseSparkAdapterCredentialFields](docs/BaseSparkAdapterCredentialFields.md)
  38. PATH_EXISTS crates/dbt-cloud-api/docs/basesparkadaptercredentialfieldsrequest.md crates/dbt-cloud-api/README.md:138-138
     tier: anchored
     raw: [BaseSparkAdapterCredentialFieldsRequest](docs/BaseSparkAdapterCredentialFieldsRequest.md)
  39. PATH_EXISTS crates/dbt-cloud-api/docs/basesparkadaptercredentialsschema.md crates/dbt-cloud-api/README.md:139-139
     tier: anchored
     raw: [BaseSparkAdapterCredentialsSchema](docs/BaseSparkAdapterCredentialsSchema.md)
  40. PATH_EXISTS crates/dbt-cloud-api/docs/basesparkadaptercredentialsschemarequest.md crates/dbt-cloud-api/README.md:140-140
     tier: anchored
     raw: [BaseSparkAdapterCredentialsSchemaRequest](docs/BaseSparkAdapterCredentialsSchemaRequest.md)
  41. PATH_EXISTS crates/dbt-cloud-api/docs/bigqueryconnection.md crates/dbt-cloud-api/README.md:141-141
     tier: anchored
     raw: [BigqueryConnection](docs/BigqueryConnection.md)
  42. PATH_EXISTS crates/dbt-cloud-api/docs/bigqueryconnectionv1.md crates/dbt-cloud-api/README.md:142-142
     tier: anchored
     raw: [BigqueryConnectionV1](docs/BigqueryConnectionV1.md)
  43. PATH_EXISTS crates/dbt-cloud-api/docs/bigquerycredentials.md crates/dbt-cloud-api/README.md:143-143
     tier: anchored
     raw: [BigqueryCredentials](docs/BigqueryCredentials.md)
  44. PATH_EXISTS crates/dbt-cloud-api/docs/bigquerycredentialsrequest.md crates/dbt-cloud-api/README.md:144-144
     tier: anchored
     raw: [BigqueryCredentialsRequest](docs/BigqueryCredentialsRequest.md)
  45. PATH_EXISTS crates/dbt-cloud-api/docs/config.md crates/dbt-cloud-api/README.md:145-145
     tier: anchored
     raw: [Config](docs/Config.md)
  46. PATH_EXISTS crates/dbt-cloud-api/docs/config1.md crates/dbt-cloud-api/README.md:146-146
     tier: anchored
     raw: [Config1](docs/Config1.md)
  47. PATH_EXISTS crates/dbt-cloud-api/docs/connectionmethod.md crates/dbt-cloud-api/README.md:147-147
     tier: anchored
     raw: [ConnectionMethod](docs/ConnectionMethod.md)
  48. PATH_EXISTS crates/dbt-cloud-api/docs/connectiontypeenum.md crates/dbt-cloud-api/README.md:148-148
     tier: anchored
     raw: [ConnectionTypeEnum](docs/ConnectionTypeEnum.md)
  49. PATH_EXISTS crates/dbt-cloud-api/docs/createmanagedrepositoryrequestrequest.md crates/dbt-cloud-api/README.md:149-149
     tier: anchored
     raw: [CreateManagedRepositoryRequestRequest](docs/CreateManagedRepositoryRequestRequest.md)
  50. PATH_EXISTS crates/dbt-cloud-api/docs/createorreplacegroupscimrequestrequest.md crates/dbt-cloud-api/README.md:150-150
     tier: anchored
     raw: [CreateOrReplaceGroupScimRequestRequest](docs/CreateOrReplaceGroupScimRequestRequest.md)
  51. PATH_EXISTS crates/dbt-cloud-api/docs/createscimconfigurationrequestrequest.md crates/dbt-cloud-api/README.md:151-151
     tier: anchored
     raw: [CreateScimConfigurationRequestRequest](docs/CreateScimConfigurationRequestRequest.md)
  52. PATH_EXISTS crates/dbt-cloud-api/docs/createscimtoken.md crates/dbt-cloud-api/README.md:152-152
     tier: anchored
     raw: [CreateScimToken](docs/CreateScimToken.md)
  53. PATH_EXISTS crates/dbt-cloud-api/docs/createscimtokenrequestrequest.md crates/dbt-cloud-api/README.md:153-153
     tier: anchored
     raw: [CreateScimTokenRequestRequest](docs/CreateScimTokenRequestRequest.md)
  54. PATH_EXISTS crates/dbt-cloud-api/docs/createservicetoken.md crates/dbt-cloud-api/README.md:154-154
     tier: anchored
     raw: [CreateServiceToken](docs/CreateServiceToken.md)
  55. PATH_EXISTS crates/dbt-cloud-api/docs/createservicetokenrequestrequest.md crates/dbt-cloud-api/README.md:155-155
     tier: anchored
     raw: [CreateServiceTokenRequestRequest](docs/CreateServiceTokenRequestRequest.md)
  56. PATH_EXISTS crates/dbt-cloud-api/docs/createsubscriptionresponseenvelope.md crates/dbt-cloud-api/README.md:156-156
     tier: anchored
     raw: [CreateSubscriptionResponseEnvelope](docs/CreateSubscriptionResponseEnvelope.md)
  57. PATH_EXISTS crates/dbt-cloud-api/docs/createuserscimrequestrequest.md crates/dbt-cloud-api/README.md:157-157
     tier: anchored
     raw: [CreateUserScimRequestRequest](docs/CreateUserScimRequestRequest.md)
  58. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsrequestrequest.md crates/dbt-cloud-api/README.md:158-158
     tier: anchored
     raw: [CredentialsRequestRequest](docs/CredentialsRequestRequest.md)
  59. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsresponse.md crates/dbt-cloud-api/README.md:159-159
     tier: anchored
     raw: [CredentialsResponse](docs/CredentialsResponse.md)
  60. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsresponseenveloped.md crates/dbt-cloud-api/README.md:160-160
     tier: anchored
     raw: [CredentialsResponseEnveloped](docs/CredentialsResponseEnveloped.md)
  61. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsresponselist.md crates/dbt-cloud-api/README.md:161-161
     tier: anchored
     raw: [CredentialsResponseList](docs/CredentialsResponseList.md)
  62. PATH_EXISTS crates/dbt-cloud-api/docs/credentialsresponselistenveloped.md crates/dbt-cloud-api/README.md:162-162
     tier: anchored
     raw: [CredentialsResponseListEnveloped](docs/CredentialsResponseListEnveloped.md)
  63. PATH_EXISTS crates/dbt-cloud-api/docs/customattributescomponent.md crates/dbt-cloud-api/README.md:163-163
     tier: anchored
     raw: [CustomAttributesComponent](docs/CustomAttributesComponent.md)
  64. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkrequest.md crates/dbt-cloud-api/README.md:164-164
     tier: anchored
     raw: [CustomEnvironmentVariableBulkRequest](docs/CustomEnvironmentVariableBulkRequest.md)
  65. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkrequestrequest.md crates/dbt-cloud-api/README.md:165-165
     tier: anchored
     raw: [CustomEnvironmentVariableBulkRequestRequest](docs/CustomEnvironmentVariableBulkRequestRequest.md)
  66. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkresponse.md crates/dbt-cloud-api/README.md:166-166
     tier: anchored
     raw: [CustomEnvironmentVariableBulkResponse](docs/CustomEnvironmentVariableBulkResponse.md)
  67. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkresponsefaillistenveloped.md crates/dbt-cloud-api/README.md:167-167
     tier: anchored
     raw: [CustomEnvironmentVariableBulkResponseFailListEnveloped](docs/CustomEnvironmentVariableBulkResponseFailListEnveloped.md)
  68. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkresponsefailresponse.md crates/dbt-cloud-api/README.md:168-168
     tier: anchored
     raw: [CustomEnvironmentVariableBulkResponseFailResponse](docs/CustomEnvironmentVariableBulkResponseFailResponse.md)
  69. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablebulkresponselistenveloped.md crates/dbt-cloud-api/README.md:169-169
     tier: anchored
     raw: [CustomEnvironmentVariableBulkResponseListEnveloped](docs/CustomEnvironmentVariableBulkResponseListEnveloped.md)
  70. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariableenveloped.md crates/dbt-cloud-api/README.md:170-170
     tier: anchored
     raw: [CustomEnvironmentVariableEnveloped](docs/CustomEnvironmentVariableEnveloped.md)
  71. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablelistenveloped.md crates/dbt-cloud-api/README.md:171-171
     tier: anchored
     raw: [CustomEnvironmentVariableListEnveloped](docs/CustomEnvironmentVariableListEnveloped.md)
  72. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariablerequest.md crates/dbt-cloud-api/README.md:172-172
     tier: anchored
     raw: [CustomEnvironmentVariableRequest](docs/CustomEnvironmentVariableRequest.md)
  73. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariableresponse.md crates/dbt-cloud-api/README.md:173-173
     tier: anchored
     raw: [CustomEnvironmentVariableResponse](docs/CustomEnvironmentVariableResponse.md)
  74. PATH_EXISTS crates/dbt-cloud-api/docs/customenvironmentvariabletypeenum.md crates/dbt-cloud-api/README.md:174-174
     tier: anchored
     raw: [CustomEnvironmentVariableTypeEnum](docs/CustomEnvironmentVariableTypeEnum.md)
  75. PATH_EXISTS crates/dbt-cloud-api/docs/custompagination.md crates/dbt-cloud-api/README.md:175-175
     tier: anchored
     raw: [CustomPagination](docs/CustomPagination.md)
  76. PATH_EXISTS crates/dbt-cloud-api/docs/databricksconnection.md crates/dbt-cloud-api/README.md:176-176
     tier: anchored
     raw: [DatabricksConnection](docs/DatabricksConnection.md)
  77. PATH_EXISTS crates/dbt-cloud-api/docs/databrickssparkconnection.md crates/dbt-cloud-api/README.md:177-177
     tier: anchored
     raw: [DatabricksSparkConnection](docs/DatabricksSparkConnection.md)
  78. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadaptercredentials.md crates/dbt-cloud-api/README.md:178-178
     tier: anchored
     raw: [DbtAdapterCredentials](docs/DbtAdapterCredentials.md)
  79. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadaptercredentialsrequest.md crates/dbt-cloud-api/README.md:179-179
     tier: anchored
     raw: [DbtAdapterCredentialsRequest](docs/DbtAdapterCredentialsRequest.md)
  80. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadapterenveloped.md crates/dbt-cloud-api/README.md:180-180
     tier: anchored
     raw: [DbtAdapterEnveloped](docs/DbtAdapterEnveloped.md)
  81. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadapterrequest.md crates/dbt-cloud-api/README.md:181-181
     tier: anchored
     raw: [DbtAdapterRequest](docs/DbtAdapterRequest.md)
  82. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadapterresponse.md crates/dbt-cloud-api/README.md:182-182
     tier: anchored
     raw: [DbtAdapterResponse](docs/DbtAdapterResponse.md)
  83. PATH_EXISTS crates/dbt-cloud-api/docs/dbtadapterversion.md crates/dbt-cloud-api/README.md:183-183
     tier: anchored
     raw: [DbtAdapterVersion](docs/DbtAdapterVersion.md)
  84. PATH_EXISTS crates/dbt-cloud-api/docs/deletesubscriptionresponsedata.md crates/dbt-cloud-api/README.md:184-184
     tier: anchored
     raw: [DeleteSubscriptionResponseData](docs/DeleteSubscriptionResponseData.md)
  85. PATH_EXISTS crates/dbt-cloud-api/docs/deletesubscriptionresponseenvelope.md crates/dbt-cloud-api/README.md:185-185
     tier: anchored
     raw: [DeleteSubscriptionResponseEnvelope](docs/DeleteSubscriptionResponseEnvelope.md)
  86. PATH_EXISTS crates/dbt-cloud-api/docs/deletesubscriptionresponsestatus.md crates/dbt-cloud-api/README.md:186-186
     tier: anchored
     raw: [DeleteSubscriptionResponseStatus](docs/DeleteSubscriptionResponseStatus.md)
  87. PATH_EXISTS crates/dbt-cloud-api/docs/deploykey.md crates/dbt-cloud-api/README.md:187-187
     tier: anchored
     raw: [DeployKey](docs/DeployKey.md)
  88. PATH_EXISTS crates/dbt-cloud-api/docs/deploymentenvironmentauthtype.md crates/dbt-cloud-api/README.md:188-188
     tier: anchored
     raw: [DeploymentEnvironmentAuthType](docs/DeploymentEnvironmentAuthType.md)
  89. PATH_EXISTS crates/dbt-cloud-api/docs/deploymenttypeenum.md crates/dbt-cloud-api/README.md:189-189
     tier: anchored
     raw: [DeploymentTypeEnum](docs/DeploymentTypeEnum.md)
  90. PATH_EXISTS crates/dbt-cloud-api/docs/detailaccountuserresponse.md crates/dbt-cloud-api/README.md:190-190
     tier: anchored
     raw: [DetailAccountUserResponse](docs/DetailAccountUserResponse.md)
  91. PATH_EXISTS crates/dbt-cloud-api/docs/detailcreatescimtokenresponse.md crates/dbt-cloud-api/README.md:191-191
     tier: anchored
     raw: [DetailCreateScimTokenResponse](docs/DetailCreateScimTokenResponse.md)
  92. PATH_EXISTS crates/dbt-cloud-api/docs/detailcreateservicetokenresponse.md crates/dbt-cloud-api/README.md:192-192
     tier: anchored
     raw: [DetailCreateServiceTokenResponse](docs/DetailCreateServiceTokenResponse.md)
  93. PATH_EXISTS crates/dbt-cloud-api/docs/detailfavoriteassetresponse.md crates/dbt-cloud-api/README.md:193-193
     tier: anchored
     raw: [DetailFavoriteAssetResponse](docs/DetailFavoriteAssetResponse.md)
  94. PATH_EXISTS crates/dbt-cloud-api/docs/detailgroupscimresponse.md crates/dbt-cloud-api/README.md:194-194
     tier: anchored
     raw: [DetailGroupScimResponse](docs/DetailGroupScimResponse.md)
  95. PATH_EXISTS crates/dbt-cloud-api/docs/detaillineageintegrationresponse.md crates/dbt-cloud-api/README.md:195-195
     tier: anchored
     raw: [DetailLineageIntegrationResponse](docs/DetailLineageIntegrationResponse.md)
  96. PATH_EXISTS crates/dbt-cloud-api/docs/detailscimconfigresponse.md crates/dbt-cloud-api/README.md:196-196
     tier: anchored
     raw: [DetailScimConfigResponse](docs/DetailScimConfigResponse.md)
  97. PATH_EXISTS crates/dbt-cloud-api/docs/detailscimlistresponse.md crates/dbt-cloud-api/README.md:197-197
     tier: anchored
     raw: [DetailScimListResponse](docs/DetailScimListResponse.md)
  98. PATH_EXISTS crates/dbt-cloud-api/docs/detailscimresourcetyperesponse.md crates/dbt-cloud-api/README.md:198-198
     tier: anchored
     raw: [DetailScimResourceTypeResponse](docs/DetailScimResourceTypeResponse.md)
  99. PATH_EXISTS crates/dbt-cloud-api/docs/detailscimtokenresponse.md crates/dbt-cloud-api/README.md:199-199
     tier: anchored
     raw: [DetailScimTokenResponse](docs/DetailScimTokenResponse.md)
  100. PATH_EXISTS crates/dbt-cloud-api/docs/detailservicetokenresponse.md crates/dbt-cloud-api/README.md:200-200
     tier: anchored
     raw: [DetailServiceTokenResponse](docs/DetailServiceTokenResponse.md)
  101. PATH_EXISTS crates/dbt-cloud-api/docs/detailuserscimresponse.md crates/dbt-cloud-api/README.md:201-201
     tier: anchored
     raw: [DetailUserScimResponse](docs/DetailUserScimResponse.md)
  102. PATH_EXISTS crates/dbt-cloud-api/docs/entraextradata.md crates/dbt-cloud-api/README.md:202-202
     tier: anchored
     raw: [EntraExtraData](docs/EntraExtraData.md)
  103. PATH_EXISTS crates/dbt-cloud-api/docs/entraextradatarequest.md crates/dbt-cloud-api/README.md:203-203
     tier: anchored
     raw: [EntraExtraDataRequest](docs/EntraExtraDataRequest.md)
  104. PATH_EXISTS crates/dbt-cloud-api/docs/environmentv3.md crates/dbt-cloud-api/README.md:204-204
     tier: anchored
     raw: [EnvironmentV3](docs/EnvironmentV3.md)
  105. PATH_EXISTS crates/dbt-cloud-api/docs/environmentv3enveloped.md crates/dbt-cloud-api/README.md:205-205
     tier: anchored
     raw: [EnvironmentV3Enveloped](docs/EnvironmentV3Enveloped.md)
  106. PATH_EXISTS crates/dbt-cloud-api/docs/environmentv3listenveloped.md crates/dbt-cloud-api/README.md:206-206
     tier: anchored
     raw: [EnvironmentV3ListEnveloped](docs/EnvironmentV3ListEnveloped.md)
  107. PATH_EXISTS crates/dbt-cloud-api/docs/environmentv3request.md crates/dbt-cloud-api/README.md:207-207
     tier: anchored
     raw: [EnvironmentV3Request](docs/EnvironmentV3Request.md)
  108. PATH_EXISTS crates/dbt-cloud-api/docs/environmentv3response.md crates/dbt-cloud-api/README.md:208-208
     tier: anchored
     raw: [EnvironmentV3Response](docs/EnvironmentV3Response.md)
  109. PATH_EXISTS crates/dbt-cloud-api/docs/event.md crates/dbt-cloud-api/README.md:209-209
     tier: anchored
     raw: [Event](docs/Event.md)
  110. PATH_EXISTS crates/dbt-cloud-api/docs/eventresponseenvelope.md crates/dbt-cloud-api/README.md:210-210
     tier: anchored
     raw: [EventResponseEnvelope](docs/EventResponseEnvelope.md)
  111. PATH_EXISTS crates/dbt-cloud-api/docs/extendedattributesenveloped.md crates/dbt-cloud-api/README.md:211-211
     tier: anchored
     raw: [ExtendedAttributesEnveloped](docs/ExtendedAttributesEnveloped.md)
  112. PATH_EXISTS crates/dbt-cloud-api/docs/extendedattributesrequest.md crates/dbt-cloud-api/README.md:212-212
     tier: anchored
     raw: [ExtendedAttributesRequest](docs/ExtendedAttributesRequest.md)
  113. PATH_EXISTS crates/dbt-cloud-api/docs/extendedattributesresponse.md crates/dbt-cloud-api/README.md:213-213
     tier: anchored
     raw: [ExtendedAttributesResponse](docs/ExtendedAttributesResponse.md)
  114. PATH_EXISTS crates/dbt-cloud-api/docs/extra.md crates/dbt-cloud-api/README.md:214-214
     tier: anchored
     raw: [Extra](docs/Extra.md)
  115. PATH_EXISTS crates/dbt-cloud-api/docs/fabricconnection.md crates/dbt-cloud-api/README.md:215-215
     tier: anchored
     raw: [FabricConnection](docs/FabricConnection.md)
  116. PATH_EXISTS crates/dbt-cloud-api/docs/favoriteasset.md crates/dbt-cloud-api/README.md:216-216
     tier: anchored
     raw: [FavoriteAsset](docs/FavoriteAsset.md)
  117. PATH_EXISTS crates/dbt-cloud-api/docs/fieldgroup.md crates/dbt-cloud-api/README.md:217-217
     tier: anchored
     raw: [FieldGroup](docs/FieldGroup.md)
  118. PATH_EXISTS crates/dbt-cloud-api/docs/fieldgrouprequest.md crates/dbt-cloud-api/README.md:218-218
     tier: anchored
     raw: [FieldGroupRequest](docs/FieldGroupRequest.md)
  119. PATH_EXISTS crates/dbt-cloud-api/docs/filters.md crates/dbt-cloud-api/README.md:219-219
     tier: anchored
     raw: [Filters](docs/Filters.md)
  120. PATH_EXISTS crates/dbt-cloud-api/docs/generictextvalidation.md crates/dbt-cloud-api/README.md:220-220
     tier: anchored
     raw: [GenericTextValidation](docs/GenericTextValidation.md)
  121. PATH_EXISTS crates/dbt-cloud-api/docs/generictextvalidationrequest.md crates/dbt-cloud-api/README.md:221-221
     tier: anchored
     raw: [GenericTextValidationRequest](docs/GenericTextValidationRequest.md)
  122. PATH_EXISTS crates/dbt-cloud-api/docs/getlineageintegrationwatchselectionresponse.md crates/dbt-cloud-api/README.md:222-222
     tier: anchored
     raw: [GetLineageIntegrationWatchSelectionResponse](docs/GetLineageIntegrationWatchSelectionResponse.md)
  123. PATH_EXISTS crates/dbt-cloud-api/docs/getwebhooksreceiptresponseenvelope.md crates/dbt-cloud-api/README.md:223-223
     tier: anchored
     raw: [GetWebhooksReceiptResponseEnvelope](docs/GetWebhooksReceiptResponseEnvelope.md)
  124. PATH_EXISTS crates/dbt-cloud-api/docs/gitclonestrategyenum.md crates/dbt-cloud-api/README.md:224-224
     tier: anchored
     raw: [GitCloneStrategyEnum](docs/GitCloneStrategyEnum.md)
  125. PATH_EXISTS crates/dbt-cloud-api/docs/group.md crates/dbt-cloud-api/README.md:225-225
     tier: anchored
     raw: [Group](docs/Group.md)
  126. PATH_EXISTS crates/dbt-cloud-api/docs/groupenveloped.md crates/dbt-cloud-api/README.md:226-226
     tier: anchored
     raw: [GroupEnveloped](docs/GroupEnveloped.md)
  127. PATH_EXISTS crates/dbt-cloud-api/docs/grouplistenveloped.md crates/dbt-cloud-api/README.md:227-227
     tier: anchored
     raw: [GroupListEnveloped](docs/GroupListEnveloped.md)
  128. PATH_EXISTS crates/dbt-cloud-api/docs/groupmembercomponent.md crates/dbt-cloud-api/README.md:228-228
     tier: anchored
     raw: [GroupMemberComponent](docs/GroupMemberComponent.md)
  129. PATH_EXISTS crates/dbt-cloud-api/docs/grouppermission.md crates/dbt-cloud-api/README.md:229-229
     tier: anchored
     raw: [GroupPermission](docs/GroupPermission.md)
  130. PATH_EXISTS crates/dbt-cloud-api/docs/grouppermissionlistenveloped.md crates/dbt-cloud-api/README.md:230-230
     tier: anchored
     raw: [GroupPermissionListEnveloped](docs/GroupPermissionListEnveloped.md)
  131. PATH_EXISTS crates/dbt-cloud-api/docs/grouppermissionlistrequest.md crates/dbt-cloud-api/README.md:231-231
     tier: anchored
     raw: [GroupPermissionListRequest](docs/GroupPermissionListRequest.md)
  132. PATH_EXISTS crates/dbt-cloud-api/docs/grouppermissionrequest.md crates/dbt-cloud-api/README.md:232-232
     tier: anchored
     raw: [GroupPermissionRequest](docs/GroupPermissionRequest.md)
  133. PATH_EXISTS crates/dbt-cloud-api/docs/grouppermissionresponse.md crates/dbt-cloud-api/README.md:233-233
     tier: anchored
     raw: [GroupPermissionResponse](docs/GroupPermissionResponse.md)
  134. PATH_EXISTS crates/dbt-cloud-api/docs/grouprequest.md crates/dbt-cloud-api/README.md:234-234
     tier: anchored
     raw: [GroupRequest](docs/GroupRequest.md)
  135. PATH_EXISTS crates/dbt-cloud-api/docs/groupresponse.md crates/dbt-cloud-api/README.md:235-235
     tier: anchored
     raw: [GroupResponse](docs/GroupResponse.md)
  136. PATH_EXISTS crates/dbt-cloud-api/docs/groupscim.md crates/dbt-cloud-api/README.md:236-236
     tier: anchored
     raw: [GroupScim](docs/GroupScim.md)
  137. PATH_EXISTS crates/dbt-cloud-api/docs/groupscimresponse.md crates/dbt-cloud-api/README.md:237-237
     tier: anchored
     raw: [GroupScimResponse](docs/GroupScimResponse.md)
  138. PATH_EXISTS crates/dbt-cloud-api/docs/humanreadabledatestrategytypeenum.md crates/dbt-cloud-api/README.md:238-238
     tier: anchored
     raw: [HumanReadableDateStrategyTypeEnum](docs/HumanReadableDateStrategyTypeEnum.md)
  139. PATH_EXISTS crates/dbt-cloud-api/docs/humanreadabletimestrategtypeenum.md crates/dbt-cloud-api/README.md:239-239
     tier: anchored
     raw: [HumanReadableTimeStrategTypeEnum](docs/HumanReadableTimeStrategTypeEnum.md)
  140. PATH_EXISTS crates/dbt-cloud-api/docs/inviteusersrequestrequest.md crates/dbt-cloud-api/README.md:240-240
     tier: anchored
     raw: [InviteUsersRequestRequest](docs/InviteUsersRequestRequest.md)
  141. PATH_EXISTS crates/dbt-cloud-api/docs/inviteusersresponse.md crates/dbt-cloud-api/README.md:241-241
     tier: anchored
     raw: [InviteUsersResponse](docs/InviteUsersResponse.md)
  142. PATH_EXISTS crates/dbt-cloud-api/docs/inviteusersresponseenveloped.md crates/dbt-cloud-api/README.md:242-242
     tier: anchored
     raw: [InviteUsersResponseEnveloped](docs/InviteUsersResponseEnveloped.md)
  143. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictioncidr.md crates/dbt-cloud-api/README.md:243-243
     tier: anchored
     raw: [IpRestrictionCidr](docs/IpRestrictionCidr.md)
  144. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictioncidrrequestrequest.md crates/dbt-cloud-api/README.md:244-244
     tier: anchored
     raw: [IpRestrictionCidrRequestRequest](docs/IpRestrictionCidrRequestRequest.md)
  145. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionrequestrequest.md crates/dbt-cloud-api/README.md:245-245
     tier: anchored
     raw: [IpRestrictionRequestRequest](docs/IpRestrictionRequestRequest.md)
  146. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionrule.md crates/dbt-cloud-api/README.md:246-246
     tier: anchored
     raw: [IpRestrictionRule](docs/IpRestrictionRule.md)
  147. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionruleenveloped.md crates/dbt-cloud-api/README.md:247-247
     tier: anchored
     raw: [IpRestrictionRuleEnveloped](docs/IpRestrictionRuleEnveloped.md)
  148. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionrulelistenveloped.md crates/dbt-cloud-api/README.md:248-248
     tier: anchored
     raw: [IpRestrictionRuleListEnveloped](docs/IpRestrictionRuleListEnveloped.md)
  149. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionruleresponse.md crates/dbt-cloud-api/README.md:249-249
     tier: anchored
     raw: [IpRestrictionRuleResponse](docs/IpRestrictionRuleResponse.md)
  150. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionrulesetenveloped.md crates/dbt-cloud-api/README.md:250-250
     tier: anchored
     raw: [IpRestrictionRuleSetEnveloped](docs/IpRestrictionRuleSetEnveloped.md)
  151. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionrulesetresponse.md crates/dbt-cloud-api/README.md:251-251
     tier: anchored
     raw: [IpRestrictionRuleSetResponse](docs/IpRestrictionRuleSetResponse.md)
  152. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionsetrequestrequest.md crates/dbt-cloud-api/README.md:252-252
     tier: anchored
     raw: [IpRestrictionSetRequestRequest](docs/IpRestrictionSetRequestRequest.md)
  153. PATH_EXISTS crates/dbt-cloud-api/docs/iprestrictionsetvalidate.md crates/dbt-cloud-api/README.md:253-253
     tier: anchored
     raw: [IpRestrictionSetValidate](docs/IpRestrictionSetValidate.md)
  154. PATH_EXISTS crates/dbt-cloud-api/docs/jobdefinitionexecution.md crates/dbt-cloud-api/README.md:254-254
     tier: anchored
     raw: [JobDefinitionExecution](docs/JobDefinitionExecution.md)
  155. PATH_EXISTS crates/dbt-cloud-api/docs/jobdefinitionschedule.md crates/dbt-cloud-api/README.md:255-255
     tier: anchored
     raw: [JobDefinitionSchedule](docs/JobDefinitionSchedule.md)
  156. PATH_EXISTS crates/dbt-cloud-api/docs/jobdefinitionsettings.md crates/dbt-cloud-api/README.md:256-256
     tier: anchored
     raw: [JobDefinitionSettings](docs/JobDefinitionSettings.md)
  157. PATH_EXISTS crates/dbt-cloud-api/docs/jobdefinitiontriggers.md crates/dbt-cloud-api/README.md:257-257
     tier: anchored
     raw: [JobDefinitionTriggers](docs/JobDefinitionTriggers.md)
  158. PATH_EXISTS crates/dbt-cloud-api/docs/jobdefinitionv2.md crates/dbt-cloud-api/README.md:258-258
     tier: anchored
     raw: [JobDefinitionV2](docs/JobDefinitionV2.md)
  159. PATH_EXISTS crates/dbt-cloud-api/docs/jobtypeenum.md crates/dbt-cloud-api/README.md:259-259
     tier: anchored
     raw: [JobTypeEnum](docs/JobTypeEnum.md)
  160. PATH_EXISTS crates/dbt-cloud-api/docs/legacyintegerfield.md crates/dbt-cloud-api/README.md:260-260
     tier: anchored
     raw: [LegacyIntegerField](docs/LegacyIntegerField.md)
  161. PATH_EXISTS crates/dbt-cloud-api/docs/legacyintegerfieldrequest.md crates/dbt-cloud-api/README.md:261-261
     tier: anchored
     raw: [LegacyIntegerFieldRequest](docs/LegacyIntegerFieldRequest.md)
  162. PATH_EXISTS crates/dbt-cloud-api/docs/licensemapenveloped.md crates/dbt-cloud-api/README.md:262-262
     tier: anchored
     raw: [LicenseMapEnveloped](docs/LicenseMapEnveloped.md)
  163. PATH_EXISTS crates/dbt-cloud-api/docs/licensemaplistenveloped.md crates/dbt-cloud-api/README.md:263-263
     tier: anchored
     raw: [LicenseMapListEnveloped](docs/LicenseMapListEnveloped.md)
  164. PATH_EXISTS crates/dbt-cloud-api/docs/licensemaprequest.md crates/dbt-cloud-api/README.md:264-264
     tier: anchored
     raw: [LicenseMapRequest](docs/LicenseMapRequest.md)
  165. PATH_EXISTS crates/dbt-cloud-api/docs/licensemapresponse.md crates/dbt-cloud-api/README.md:265-265
     tier: anchored
     raw: [LicenseMapResponse](docs/LicenseMapResponse.md)
  166. PATH_EXISTS crates/dbt-cloud-api/docs/licensetype.md crates/dbt-cloud-api/README.md:266-266
     tier: anchored
     raw: [LicenseType](docs/LicenseType.md)
  167. PATH_EXISTS crates/dbt-cloud-api/docs/licensetypeenum.md crates/dbt-cloud-api/README.md:267-267
     tier: anchored
     raw: [LicenseTypeEnum](docs/LicenseTypeEnum.md)
  168. PATH_EXISTS crates/dbt-cloud-api/docs/lineageintegration.md crates/dbt-cloud-api/README.md:268-268
     tier: anchored
     raw: [LineageIntegration](docs/LineageIntegration.md)
  169. PATH_EXISTS crates/dbt-cloud-api/docs/lineageintegrationcollection.md crates/dbt-cloud-api/README.md:269-269
     tier: anchored
     raw: [LineageIntegrationCollection](docs/LineageIntegrationCollection.md)
  170. PATH_EXISTS crates/dbt-cloud-api/docs/lineageintegrationtype.md crates/dbt-cloud-api/README.md:270-270
     tier: anchored
     raw: [LineageIntegrationType](docs/LineageIntegrationType.md)
  171. PATH_EXISTS crates/dbt-cloud-api/docs/listgroupscimresponse.md crates/dbt-cloud-api/README.md:271-271
     tier: anchored
     raw: [ListGroupScimResponse](docs/ListGroupScimResponse.md)
  172. PATH_EXISTS crates/dbt-cloud-api/docs/listlineageintegrationcollectionresponse.md crates/dbt-cloud-api/README.md:272-272
     tier: anchored
     raw: [ListLineageIntegrationCollectionResponse](docs/ListLineageIntegrationCollectionResponse.md)
  173. PATH_EXISTS crates/dbt-cloud-api/docs/listlineageintegrationresponse.md crates/dbt-cloud-api/README.md:273-273
     tier: anchored
     raw: [ListLineageIntegrationResponse](docs/ListLineageIntegrationResponse.md)
  174. PATH_EXISTS crates/dbt-cloud-api/docs/listscimtokenresponse.md crates/dbt-cloud-api/README.md:274-274
     tier: anchored
     raw: [ListScimTokenResponse](docs/ListScimTokenResponse.md)
  175. PATH_EXISTS crates/dbt-cloud-api/docs/listservicetokenresponse.md crates/dbt-cloud-api/README.md:275-275
     tier: anchored
     raw: [ListServiceTokenResponse](docs/ListServiceTokenResponse.md)
  176. PATH_EXISTS crates/dbt-cloud-api/docs/listuserscimresponse.md crates/dbt-cloud-api/README.md:276-276
     tier: anchored
     raw: [ListUserScimResponse](docs/ListUserScimResponse.md)
  177. PATH_EXISTS crates/dbt-cloud-api/docs/listwebhooksreceiptsresponseenvelope.md crates/dbt-cloud-api/README.md:277-277
     tier: anchored
     raw: [ListWebhooksReceiptsResponseEnvelope](docs/ListWebhooksReceiptsResponseEnvelope.md)
  178. PATH_EXISTS crates/dbt-cloud-api/docs/lockcauseenum.md crates/dbt-cloud-api/README.md:278-278
     tier: anchored
     raw: [LockCauseEnum](docs/LockCauseEnum.md)
  179. PATH_EXISTS crates/dbt-cloud-api/docs/metacomponent.md crates/dbt-cloud-api/README.md:279-279
     tier: anchored
     raw: [MetaComponent](docs/MetaComponent.md)
  180. PATH_EXISTS crates/dbt-cloud-api/docs/method.md crates/dbt-cloud-api/README.md:280-280
     tier: anchored
     raw: [Method](docs/Method.md)
  181. PATH_EXISTS crates/dbt-cloud-api/docs/notfound.md crates/dbt-cloud-api/README.md:281-281
     tier: anchored
     raw: [NotFound](docs/NotFound.md)
  182. PATH_EXISTS crates/dbt-cloud-api/docs/notfoundstatus.md crates/dbt-cloud-api/README.md:282-282
     tier: anchored
     raw: [NotFoundStatus](docs/NotFoundStatus.md)
  183. PATH_EXISTS crates/dbt-cloud-api/docs/oauthconfigurationenveloped.md crates/dbt-cloud-api/README.md:283-283
     tier: anchored
     raw: [OAuthConfigurationEnveloped](docs/OAuthConfigurationEnveloped.md)
  184. PATH_EXISTS crates/dbt-cloud-api/docs/oauthconfigurationlistenveloped.md crates/dbt-cloud-api/README.md:284-284
     tier: anchored
     raw: [OAuthConfigurationListEnveloped](docs/OAuthConfigurationListEnveloped.md)
  185. PATH_EXISTS crates/dbt-cloud-api/docs/oauthconfigurationrequest.md crates/dbt-cloud-api/README.md:285-285
     tier: anchored
     raw: [OAuthConfigurationRequest](docs/OAuthConfigurationRequest.md)
  186. PATH_EXISTS crates/dbt-cloud-api/docs/oauthconfigurationresponse.md crates/dbt-cloud-api/README.md:286-286
     tier: anchored
     raw: [OAuthConfigurationResponse](docs/OAuthConfigurationResponse.md)
  187. PATH_EXISTS crates/dbt-cloud-api/docs/optionalapachesparkconnection.md crates/dbt-cloud-api/README.md:287-287
     tier: anchored
     raw: [OptionalApacheSparkConnection](docs/OptionalApacheSparkConnection.md)
  188. PATH_EXISTS crates/dbt-cloud-api/docs/optionalathenaconnection.md crates/dbt-cloud-api/README.md:288-288
     tier: anchored
     raw: [OptionalAthenaConnection](docs/OptionalAthenaConnection.md)
  189. PATH_EXISTS crates/dbt-cloud-api/docs/optionalbigqueryconnection.md crates/dbt-cloud-api/README.md:289-289
     tier: anchored
     raw: [OptionalBigqueryConnection](docs/OptionalBigqueryConnection.md)
  190. PATH_EXISTS crates/dbt-cloud-api/docs/optionalbigqueryconnectionv1.md crates/dbt-cloud-api/README.md:290-290
     tier: anchored
     raw: [OptionalBigqueryConnectionV1](docs/OptionalBigqueryConnectionV1.md)
  191. PATH_EXISTS crates/dbt-cloud-api/docs/optionaldatabricksconnection.md crates/dbt-cloud-api/README.md:291-291
     tier: anchored
     raw: [OptionalDatabricksConnection](docs/OptionalDatabricksConnection.md)
  192. PATH_EXISTS crates/dbt-cloud-api/docs/optionaldatabrickssparkconnection.md crates/dbt-cloud-api/README.md:292-292
     tier: anchored
     raw: [OptionalDatabricksSparkConnection](docs/OptionalDatabricksSparkConnection.md)
  193. PATH_EXISTS crates/dbt-cloud-api/docs/optionalfabricconnection.md crates/dbt-cloud-api/README.md:293-293
     tier: anchored
     raw: [OptionalFabricConnection](docs/OptionalFabricConnection.md)
  194. PATH_EXISTS crates/dbt-cloud-api/docs/optionalpostgresconnection.md crates/dbt-cloud-api/README.md:294-294
     tier: anchored
     raw: [OptionalPostgresConnection](docs/OptionalPostgresConnection.md)
  195. PATH_EXISTS crates/dbt-cloud-api/docs/optionalredshiftconnection.md crates/dbt-cloud-api/README.md:295-295
     tier: anchored
     raw: [OptionalRedshiftConnection](docs/OptionalRedshiftConnection.md)
  196. PATH_EXISTS crates/dbt-cloud-api/docs/optionalsnowflakeconnection.md crates/dbt-cloud-api/README.md:296-296
     tier: anchored
     raw: [OptionalSnowflakeConnection](docs/OptionalSnowflakeConnection.md)
  197. PATH_EXISTS crates/dbt-cloud-api/docs/optionalsynapseconnection.md crates/dbt-cloud-api/README.md:297-297
     tier: anchored
     raw: [OptionalSynapseConnection](docs/OptionalSynapseConnection.md)
  198. PATH_EXISTS crates/dbt-cloud-api/docs/optionalteradataconnection.md crates/dbt-cloud-api/README.md:298-298
     tier: anchored
     raw: [OptionalTeradataConnection](docs/OptionalTeradataConnection.md)
  199. PATH_EXISTS crates/dbt-cloud-api/docs/optionaltrinoconnection.md crates/dbt-cloud-api/README.md:299-299
     tier: anchored
     raw: [OptionalTrinoConnection](docs/OptionalTrinoConnection.md)
  200. PATH_EXISTS crates/dbt-cloud-api/docs/orderby.md crates/dbt-cloud-api/README.md:300-300
     tier: anchored
     raw: [OrderBy](docs/OrderBy.md)
  201. PATH_EXISTS crates/dbt-cloud-api/docs/paginatedwebhooksevents.md crates/dbt-cloud-api/README.md:301-301
     tier: anchored
     raw: [PaginatedWebhooksEvents](docs/PaginatedWebhooksEvents.md)
  202. PATH_EXISTS crates/dbt-cloud-api/docs/paginatedwebhookssubscriptions.md crates/dbt-cloud-api/README.md:302-302
     tier: anchored
     raw: [PaginatedWebhooksSubscriptions](docs/PaginatedWebhooksSubscriptions.md)
  203. PATH_EXISTS crates/dbt-cloud-api/docs/pagination.md crates/dbt-cloud-api/README.md:303-303
     tier: anchored
     raw: [Pagination](docs/Pagination.md)
  204. PATH_EXISTS crates/dbt-cloud-api/docs/paginationextra.md crates/dbt-cloud-api/README.md:304-304
     tier: anchored
     raw: [PaginationExtra](docs/PaginationExtra.md)
  205. PATH_EXISTS crates/dbt-cloud-api/docs/patchgroupscimrequestrequest.md crates/dbt-cloud-api/README.md:305-305
     tier: anchored
     raw: [PatchGroupScimRequestRequest](docs/PatchGroupScimRequestRequest.md)
  206. PATH_EXISTS crates/dbt-cloud-api/docs/patchlineageintegrationrequest.md crates/dbt-cloud-api/README.md:306-306
     tier: anchored
     raw: [PatchLineageIntegrationRequest](docs/PatchLineageIntegrationRequest.md)
  207. PATH_EXISTS crates/dbt-cloud-api/docs/patchop.md crates/dbt-cloud-api/README.md:307-307
     tier: anchored
     raw: [PatchOp](docs/PatchOp.md)
  208. PATH_EXISTS crates/dbt-cloud-api/docs/patchoperation.md crates/dbt-cloud-api/README.md:308-308
     tier: anchored
     raw: [PatchOperation](docs/PatchOperation.md)
  209. PATH_EXISTS crates/dbt-cloud-api/docs/permissionsetenum.md crates/dbt-cloud-api/README.md:309-309
     tier: anchored
     raw: [PermissionSetEnum](docs/PermissionSetEnum.md)
  210. PATH_EXISTS crates/dbt-cloud-api/docs/planenum.md crates/dbt-cloud-api/README.md:310-310
     tier: anchored
     raw: [PlanEnum](docs/PlanEnum.md)
  211. PATH_EXISTS crates/dbt-cloud-api/docs/postlineageintegrationrequest.md crates/dbt-cloud-api/README.md:311-311
     tier: anchored
     raw: [PostLineageIntegrationRequest](docs/PostLineageIntegrationRequest.md)
  212. PATH_EXISTS crates/dbt-cloud-api/docs/postlineageintegrationwatchselectionrequest.md crates/dbt-cloud-api/README.md:312-312
     tier: anchored
     raw: [PostLineageIntegrationWatchSelectionRequest](docs/PostLineageIntegrationWatchSelectionRequest.md)
  213. PATH_EXISTS crates/dbt-cloud-api/docs/postgresconnection.md crates/dbt-cloud-api/README.md:313-313
     tier: anchored
     raw: [PostgresConnection](docs/PostgresConnection.md)
  214. PATH_EXISTS crates/dbt-cloud-api/docs/postgrescredentials.md crates/dbt-cloud-api/README.md:314-314
     tier: anchored
     raw: [PostgresCredentials](docs/PostgresCredentials.md)
  215. PATH_EXISTS crates/dbt-cloud-api/docs/postgrescredentialsrequest.md crates/dbt-cloud-api/README.md:315-315
     tier: anchored
     raw: [PostgresCredentialsRequest](docs/PostgresCredentialsRequest.md)
  216. PATH_EXISTS crates/dbt-cloud-api/docs/predefinedpermissionset.md crates/dbt-cloud-api/README.md:316-316
     tier: anchored
     raw: [PredefinedPermissionSet](docs/PredefinedPermissionSet.md)
  217. PATH_EXISTS crates/dbt-cloud-api/docs/privatelinkendpointlistenveloped.md crates/dbt-cloud-api/README.md:317-317
     tier: anchored
     raw: [PrivateLinkEndpointListEnveloped](docs/PrivateLinkEndpointListEnveloped.md)
  218. PATH_EXISTS crates/dbt-cloud-api/docs/privatelinkendpointresponse.md crates/dbt-cloud-api/README.md:318-318
     tier: anchored
     raw: [PrivateLinkEndpointResponse](docs/PrivateLinkEndpointResponse.md)
  219. PATH_EXISTS crates/dbt-cloud-api/docs/project.md crates/dbt-cloud-api/README.md:319-319
     tier: anchored
     raw: [Project](docs/Project.md)
  220. PATH_EXISTS crates/dbt-cloud-api/docs/projectenveloped.md crates/dbt-cloud-api/README.md:320-320
     tier: anchored
     raw: [ProjectEnveloped](docs/ProjectEnveloped.md)
  221. PATH_EXISTS crates/dbt-cloud-api/docs/projectlistenveloped.md crates/dbt-cloud-api/README.md:321-321
     tier: anchored
     raw: [ProjectListEnveloped](docs/ProjectListEnveloped.md)
  222. PATH_EXISTS crates/dbt-cloud-api/docs/projectrequest.md crates/dbt-cloud-api/README.md:322-322
     tier: anchored
     raw: [ProjectRequest](docs/ProjectRequest.md)
  223. PATH_EXISTS crates/dbt-cloud-api/docs/projectresponse.md crates/dbt-cloud-api/README.md:323-323
     tier: anchored
     raw: [ProjectResponse](docs/ProjectResponse.md)
  224. PATH_EXISTS crates/dbt-cloud-api/docs/publicauditloglistenveloped.md crates/dbt-cloud-api/README.md:324-324
     tier: anchored
     raw: [PublicAuditLogListEnveloped](docs/PublicAuditLogListEnveloped.md)
  225. PATH_EXISTS crates/dbt-cloud-api/docs/publicauditlogresponse.md crates/dbt-cloud-api/README.md:325-325
     tier: anchored
     raw: [PublicAuditLogResponse](docs/PublicAuditLogResponse.md)
  226. PATH_EXISTS crates/dbt-cloud-api/docs/receipt.md crates/dbt-cloud-api/README.md:326-326
     tier: anchored
     raw: [Receipt](docs/Receipt.md)
  227. PATH_EXISTS crates/dbt-cloud-api/docs/redshiftconnection.md crates/dbt-cloud-api/README.md:327-327
     tier: anchored
     raw: [RedshiftConnection](docs/RedshiftConnection.md)
  228. PATH_EXISTS crates/dbt-cloud-api/docs/redshiftcredentials.md crates/dbt-cloud-api/README.md:328-328
     tier: anchored
     raw: [RedshiftCredentials](docs/RedshiftCredentials.md)
  229. PATH_EXISTS crates/dbt-cloud-api/docs/redshiftcredentialsauthtypeenum.md crates/dbt-cloud-api/README.md:329-329
     tier: anchored
     raw: [RedshiftCredentialsAuthTypeEnum](docs/RedshiftCredentialsAuthTypeEnum.md)
  230. PATH_EXISTS crates/dbt-cloud-api/docs/redshiftcredentialsrequest.md crates/dbt-cloud-api/README.md:330-330
     tier: anchored
     raw: [RedshiftCredentialsRequest](docs/RedshiftCredentialsRequest.md)
  231. PATH_EXISTS crates/dbt-cloud-api/docs/remotebackendenum.md crates/dbt-cloud-api/README.md:331-331
     tier: anchored
     raw: [RemoteBackendEnum](docs/RemoteBackendEnum.md)
  232. PATH_EXISTS crates/dbt-cloud-api/docs/replaceuserscimrequestrequest.md crates/dbt-cloud-api/README.md:332-332
     tier: anchored
     raw: [ReplaceUserScimRequestRequest](docs/ReplaceUserScimRequestRequest.md)
  233. PATH_EXISTS crates/dbt-cloud-api/docs/repositorygitlab.md crates/dbt-cloud-api/README.md:333-333
     tier: anchored
     raw: [RepositoryGitlab](docs/RepositoryGitlab.md)
  234. PATH_EXISTS crates/dbt-cloud-api/docs/repositoryv3.md crates/dbt-cloud-api/README.md:334-334
     tier: anchored
     raw: [RepositoryV3](docs/RepositoryV3.md)
  235. PATH_EXISTS crates/dbt-cloud-api/docs/repositoryv3enveloped.md crates/dbt-cloud-api/README.md:335-335
     tier: anchored
     raw: [RepositoryV3Enveloped](docs/RepositoryV3Enveloped.md)
  236. PATH_EXISTS crates/dbt-cloud-api/docs/repositoryv3listenveloped.md crates/dbt-cloud-api/README.md:336-336
     tier: anchored
     raw: [RepositoryV3ListEnveloped](docs/RepositoryV3ListEnveloped.md)
  237. PATH_EXISTS crates/dbt-cloud-api/docs/repositoryv3request.md crates/dbt-cloud-api/README.md:337-337
     tier: anchored
     raw: [RepositoryV3Request](docs/RepositoryV3Request.md)
  238. PATH_EXISTS crates/dbt-cloud-api/docs/repositoryv3response.md crates/dbt-cloud-api/README.md:338-338
     tier: anchored
     raw: [RepositoryV3Response](docs/RepositoryV3Response.md)
  239. PATH_EXISTS crates/dbt-cloud-api/docs/responsedata.md crates/dbt-cloud-api/README.md:339-339
     tier: anchored
     raw: [ResponseData](docs/ResponseData.md)
  240. PATH_EXISTS crates/dbt-cloud-api/docs/responsestatus.md crates/dbt-cloud-api/README.md:340-340
     tier: anchored
     raw: [ResponseStatus](docs/ResponseStatus.md)
  241. PATH_EXISTS crates/dbt-cloud-api/docs/schema.md crates/dbt-cloud-api/README.md:341-341
     tier: anchored
     raw: [Schema](docs/Schema.md)
  242. PATH_EXISTS crates/dbt-cloud-api/docs/schematypeenum.md crates/dbt-cloud-api/README.md:342-342
     tier: anchored
     raw: [SchemaTypeEnum](docs/SchemaTypeEnum.md)
  243. PATH_EXISTS crates/dbt-cloud-api/docs/schemasadaptersbigqueryv0connectionschemapriority.md crates/dbt-cloud-api/README.md:343-343
     tier: anchored
     raw: [SchemasAdaptersBigqueryV0ConnectionSchemaPriority](docs/SchemasAdaptersBigqueryV0ConnectionSchemaPriority.md)
  244. PATH_EXISTS crates/dbt-cloud-api/docs/schemasadaptersbigqueryv1connectionschemapriority.md crates/dbt-cloud-api/README.md:344-344
     tier: anchored
     raw: [SchemasAdaptersBigqueryV1ConnectionSchemaPriority](docs/SchemasAdaptersBigqueryV1ConnectionSchemaPriority.md)
  245. PATH_EXISTS crates/dbt-cloud-api/docs/scimconfig.md crates/dbt-cloud-api/README.md:345-345
     tier: anchored
     raw: [ScimConfig](docs/ScimConfig.md)
  246. PATH_EXISTS crates/dbt-cloud-api/docs/scimlist.md crates/dbt-cloud-api/README.md:346-346
     tier: anchored
     raw: [ScimList](docs/ScimList.md)
  247. PATH_EXISTS crates/dbt-cloud-api/docs/scimresourcetype.md crates/dbt-cloud-api/README.md:347-347
     tier: anchored
     raw: [ScimResourceType](docs/ScimResourceType.md)
  248. PATH_EXISTS crates/dbt-cloud-api/docs/scimtoken.md crates/dbt-cloud-api/README.md:348-348
     tier: anchored
     raw: [ScimToken](docs/ScimToken.md)
  249. PATH_EXISTS crates/dbt-cloud-api/docs/semanticlayercredentialslistenveloped.md crates/dbt-cloud-api/README.md:349-349
     tier: anchored
     raw: [SemanticLayerCredentialsListEnveloped](docs/SemanticLayerCredentialsListEnveloped.md)
  250. PATH_EXISTS crates/dbt-cloud-api/docs/semanticlayercredentialsresponse.md crates/dbt-cloud-api/README.md:350-350
     tier: anchored
     raw: [SemanticLayerCredentialsResponse](docs/SemanticLayerCredentialsResponse.md)
  251. PATH_EXISTS crates/dbt-cloud-api/docs/servicetoken.md crates/dbt-cloud-api/README.md:351-351
     tier: anchored
     raw: [ServiceToken](docs/ServiceToken.md)
  252. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenenveloped.md crates/dbt-cloud-api/README.md:352-352
     tier: anchored
     raw: [ServiceTokenEnveloped](docs/ServiceTokenEnveloped.md)
  253. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenlistenveloped.md crates/dbt-cloud-api/README.md:353-353
     tier: anchored
     raw: [ServiceTokenListEnveloped](docs/ServiceTokenListEnveloped.md)
  254. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenlite.md crates/dbt-cloud-api/README.md:354-354
     tier: anchored
     raw: [ServiceTokenLite](docs/ServiceTokenLite.md)
  255. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenpermission.md crates/dbt-cloud-api/README.md:355-355
     tier: anchored
     raw: [ServiceTokenPermission](docs/ServiceTokenPermission.md)
  256. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenpermissiongrant.md crates/dbt-cloud-api/README.md:356-356
     tier: anchored
     raw: [ServiceTokenPermissionGrant](docs/ServiceTokenPermissionGrant.md)
  257. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenpermissionlistenveloped.md crates/dbt-cloud-api/README.md:357-357
     tier: anchored
     raw: [ServiceTokenPermissionListEnveloped](docs/ServiceTokenPermissionListEnveloped.md)
  258. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenpermissionresponse.md crates/dbt-cloud-api/README.md:358-358
     tier: anchored
     raw: [ServiceTokenPermissionResponse](docs/ServiceTokenPermissionResponse.md)
  259. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokenresponse.md crates/dbt-cloud-api/README.md:359-359
     tier: anchored
     raw: [ServiceTokenResponse](docs/ServiceTokenResponse.md)
  260. PATH_EXISTS crates/dbt-cloud-api/docs/servicetokentype.md crates/dbt-cloud-api/README.md:360-360
     tier: anchored
     raw: [ServiceTokenType](docs/ServiceTokenType.md)
  261. PATH_EXISTS crates/dbt-cloud-api/docs/snowflakeconnection.md crates/dbt-cloud-api/README.md:361-361
     tier: anchored
     raw: [SnowflakeConnection](docs/SnowflakeConnection.md)
  262. PATH_EXISTS crates/dbt-cloud-api/docs/snowflakecredentials.md crates/dbt-cloud-api/README.md:362-362
     tier: anchored
     raw: [SnowflakeCredentials](docs/SnowflakeCredentials.md)
  263. PATH_EXISTS crates/dbt-cloud-api/docs/snowflakecredentialsauthtypeenum.md crates/dbt-cloud-api/README.md:363-363
     tier: anchored
     raw: [SnowflakeCredentialsAuthTypeEnum](docs/SnowflakeCredentialsAuthTypeEnum.md)
  264. PATH_EXISTS crates/dbt-cloud-api/docs/snowflakecredentialsrequest.md crates/dbt-cloud-api/README.md:364-364
     tier: anchored
     raw: [SnowflakeCredentialsRequest](docs/SnowflakeCredentialsRequest.md)
  265. PATH_EXISTS crates/dbt-cloud-api/docs/status.md crates/dbt-cloud-api/README.md:365-365
     tier: anchored
     raw: [Status](docs/Status.md)
  266. PATH_EXISTS crates/dbt-cloud-api/docs/subscription.md crates/dbt-cloud-api/README.md:366-366
     tier: anchored
     raw: [Subscription](docs/Subscription.md)
  267. PATH_EXISTS crates/dbt-cloud-api/docs/subscriptionrequest.md crates/dbt-cloud-api/README.md:367-367
     tier: anchored
     raw: [SubscriptionRequest](docs/SubscriptionRequest.md)
  268. PATH_EXISTS crates/dbt-cloud-api/docs/subscriptionresponseenvelope.md crates/dbt-cloud-api/README.md:368-368
     tier: anchored
     raw: [SubscriptionResponseEnvelope](docs/SubscriptionResponseEnvelope.md)
  269. PATH_EXISTS crates/dbt-cloud-api/docs/synapseconnection.md crates/dbt-cloud-api/README.md:369-369
     tier: anchored
     raw: [SynapseConnection](docs/SynapseConnection.md)
  270. PATH_EXISTS crates/dbt-cloud-api/docs/teradataconnection.md crates/dbt-cloud-api/README.md:370-370
     tier: anchored
     raw: [TeradataConnection](docs/TeradataConnection.md)
  271. PATH_EXISTS crates/dbt-cloud-api/docs/testsubscriptionresponsedata.md crates/dbt-cloud-api/README.md:371-371
     tier: anchored
     raw: [TestSubscriptionResponseData](docs/TestSubscriptionResponseData.md)
  272. PATH_EXISTS crates/dbt-cloud-api/docs/testsubscriptionresponseenvelope.md crates/dbt-cloud-api/README.md:372-372
     tier: anchored
     raw: [TestSubscriptionResponseEnvelope](docs/TestSubscriptionResponseEnvelope.md)
  273. PATH_EXISTS crates/dbt-cloud-api/docs/textfield.md crates/dbt-cloud-api/README.md:373-373
     tier: anchored
     raw: [TextField](docs/TextField.md)
  274. PATH_EXISTS crates/dbt-cloud-api/docs/textfieldmetadata.md crates/dbt-cloud-api/README.md:374-374
     tier: anchored
     raw: [TextFieldMetadata](docs/TextFieldMetadata.md)
  275. PATH_EXISTS crates/dbt-cloud-api/docs/textfieldmetadatarequest.md crates/dbt-cloud-api/README.md:375-375
     tier: anchored
     raw: [TextFieldMetadataRequest](docs/TextFieldMetadataRequest.md)
  276. PATH_EXISTS crates/dbt-cloud-api/docs/textfieldrequest.md crates/dbt-cloud-api/README.md:376-376
     tier: anchored
     raw: [TextFieldRequest](docs/TextFieldRequest.md)
  277. PATH_EXISTS crates/dbt-cloud-api/docs/trinoconnection.md crates/dbt-cloud-api/README.md:377-377
     tier: anchored
     raw: [TrinoConnection](docs/TrinoConnection.md)
  278. PATH_EXISTS crates/dbt-cloud-api/docs/type24eenum.md crates/dbt-cloud-api/README.md:378-378
     tier: anchored
     raw: [Type24eEnum](docs/Type24eEnum.md)
  279. PATH_EXISTS crates/dbt-cloud-api/docs/type34eenum.md crates/dbt-cloud-api/README.md:379-379
     tier: anchored
     raw: [Type34eEnum](docs/Type34eEnum.md)
  280. PATH_EXISTS crates/dbt-cloud-api/docs/type76eenum.md crates/dbt-cloud-api/README.md:380-380
     tier: anchored
     raw: [Type76eEnum](docs/Type76eEnum.md)
  281. PATH_EXISTS crates/dbt-cloud-api/docs/typeedaenum.md crates/dbt-cloud-api/README.md:381-381
     tier: anchored
     raw: [TypeEdaEnum](docs/TypeEdaEnum.md)
  282. PATH_EXISTS crates/dbt-cloud-api/docs/updateiprestrictionrequestrequest.md crates/dbt-cloud-api/README.md:382-382
     tier: anchored
     raw: [UpdateIpRestrictionRequestRequest](docs/UpdateIpRestrictionRequestRequest.md)
  283. PATH_EXISTS crates/dbt-cloud-api/docs/updateservicetokenrequestrequest.md crates/dbt-cloud-api/README.md:383-383
     tier: anchored
     raw: [UpdateServiceTokenRequestRequest](docs/UpdateServiceTokenRequestRequest.md)
  284. PATH_EXISTS crates/dbt-cloud-api/docs/updatesubscriptionresponseenvelope.md crates/dbt-cloud-api/README.md:384-384
     tier: anchored
     raw: [UpdateSubscriptionResponseEnvelope](docs/UpdateSubscriptionResponseEnvelope.md)
  285. PATH_EXISTS crates/dbt-cloud-api/docs/updateuserscimrequestrequest.md crates/dbt-cloud-api/README.md:385-385
     tier: anchored
     raw: [UpdateUserScimRequestRequest](docs/UpdateUserScimRequestRequest.md)
  286. PATH_EXISTS crates/dbt-cloud-api/docs/user.md crates/dbt-cloud-api/README.md:386-386
     tier: anchored
     raw: [User](docs/User.md)
  287. PATH_EXISTS crates/dbt-cloud-api/docs/usercredentialsenveloped.md crates/dbt-cloud-api/README.md:387-387
     tier: anchored
     raw: [UserCredentialsEnveloped](docs/UserCredentialsEnveloped.md)
  288. PATH_EXISTS crates/dbt-cloud-api/docs/usercredentialslistenveloped.md crates/dbt-cloud-api/README.md:388-388
     tier: anchored
     raw: [UserCredentialsListEnveloped](docs/UserCredentialsListEnveloped.md)
  289. PATH_EXISTS crates/dbt-cloud-api/docs/usercredentialsrequest.md crates/dbt-cloud-api/README.md:389-389
     tier: anchored
     raw: [UserCredentialsRequest](docs/UserCredentialsRequest.md)
  290. PATH_EXISTS crates/dbt-cloud-api/docs/usercredentialsresponse.md crates/dbt-cloud-api/README.md:390-390
     tier: anchored
     raw: [UserCredentialsResponse](docs/UserCredentialsResponse.md)
  291. PATH_EXISTS crates/dbt-cloud-api/docs/useremailcomponent.md crates/dbt-cloud-api/README.md:391-391
     tier: anchored
     raw: [UserEmailComponent](docs/UserEmailComponent.md)
  292. PATH_EXISTS crates/dbt-cloud-api/docs/userlicense.md crates/dbt-cloud-api/README.md:392-392
     tier: anchored
     raw: [UserLicense](docs/UserLicense.md)
  293. PATH_EXISTS crates/dbt-cloud-api/docs/userlistenveloped.md crates/dbt-cloud-api/README.md:393-393
     tier: anchored
     raw: [UserListEnveloped](docs/UserListEnveloped.md)
  294. PATH_EXISTS crates/dbt-cloud-api/docs/usernamecomponent.md crates/dbt-cloud-api/README.md:394-394
     tier: anchored
     raw: [UserNameComponent](docs/UserNameComponent.md)
  295. PATH_EXISTS crates/dbt-cloud-api/docs/useroperationcomponent.md crates/dbt-cloud-api/README.md:395-395
     tier: anchored
     raw: [UserOperationComponent](docs/UserOperationComponent.md)
  296. PATH_EXISTS crates/dbt-cloud-api/docs/userresponse.md crates/dbt-cloud-api/README.md:396-396
     tier: anchored
     raw: [UserResponse](docs/UserResponse.md)
  297. PATH_EXISTS crates/dbt-cloud-api/docs/userscim.md crates/dbt-cloud-api/README.md:397-397
     tier: anchored
     raw: [UserScim](docs/UserScim.md)
  298. PATH_EXISTS crates/dbt-cloud-api/docs/uservaluecomponent.md crates/dbt-cloud-api/README.md:398-398
     tier: anchored
     raw: [UserValueComponent](docs/UserValueComponent.md)
  299. PATH_EXISTS crates/dbt-cloud-api/docs/v3responseextradata.md crates/dbt-cloud-api/README.md:399-399
     tier: anchored
     raw: [V3ResponseExtraData](docs/V3ResponseExtraData.md)
  300. PATH_EXISTS crates/dbt-cloud-api/docs/v3responsepagination.md crates/dbt-cloud-api/README.md:400-400
     tier: anchored
     raw: [V3ResponsePagination](docs/V3ResponsePagination.md)
  301. PATH_EXISTS crates/dbt-cloud-api/docs/value.md crates/dbt-cloud-api/README.md:401-401
     tier: anchored
     raw: [Value](docs/Value.md)
  302. PATH_EXISTS crates/dbt-cloud-api/docs/watchselectionitem.md crates/dbt-cloud-api/README.md:402-402
     tier: anchored
     raw: [WatchSelectionItem](docs/WatchSelectionItem.md)
  303. PATH_EXISTS crates/dbt-cloud-api/docs/watchselectiontype.md crates/dbt-cloud-api/README.md:403-403
     tier: anchored
     raw: [WatchSelectionType](docs/WatchSelectionType.md)
  304. PATH_EXISTS crates/dbt-cloud-api/docs/webhookresponsestatus.md crates/dbt-cloud-api/README.md:404-404
     tier: anchored
     raw: [WebhookResponseStatus](docs/WebhookResponseStatus.md)
  305. PATH_EXISTS crates/dbt-telemetry-private/ crates/dbt-common/src/tracing/README.md:19-19
     tier: anchored
     raw: registry live in `crates/dbt-telemetry-private/`.
  306. PATH_EXISTS query_log.sql crates/dbt-common/src/tracing/README.md:181-181
     tier: bare
     raw: Query log: `query_log.sql`, enabled by query logging and written under the
     cited by 2 claims
  307. PATH_EXISTS crates/dbt-cli/tests/otel/telemetry_snapshot.rs crates/dbt-common/src/tracing/README.md:195-195
     tier: anchored
     raw: `crates/dbt-cli/tests/otel/telemetry_snapshot.rs`. Do not add new telemetry
  308. PATH_EXISTS dbt-common/dbt_common/clients/agate_helper.py crates/dbt-csv/README.md:7-7
     tier: unanchored
     raw: Core's CSV parsing leverages Python's `agate` library via `dbt-common/dbt_common/clients/agate_helper.py`. The parsing pipeline consists of three step
  309. PATH_EXISTS src/handlers/json.rs crates/dbt-docs-server/API-CONTRACTS.md:100-100
     tier: unanchored
     raw: Rule JSON-string parquet columns (`meta`, `config`, `type_params`, `query_params`, `exports`, `arguments`, `agg_params`, `validity_params`, `metric_fi
  310. SYMBOL_EXISTS dbt.catalog_stats crates/dbt-docs-server/API-CONTRACTS.md:444-444
     tier: -
     raw: do not exist in `catalog_tables`; they live in `dbt.catalog_stats` keyed by adapter
     evidence: module:crates.dbt-metadata-parquet.src.catalog_stats:crates/dbt-metadata-parquet/src/catalog_stats.rs
     cited by 2 claims
  311. PATH_EXISTS testview.tsx crates/dbt-docs-server/API-CONTRACTS.md:480-480
     tier: bare
     raw: dedicated UI page (currently both render via `TestView.tsx`).
     cited by 3 claims
  312. PATH_EXISTS src/handlers/pagination.rs crates/dbt-docs-server/API-CONTRACTS.md:707-707
     tier: unanchored
     raw: For `:desc` sorts and nullable sort columns the predicate uses an OR-of-conjunctions form to handle NULL bucketing correctly; see the shared `src/hand
     cited by 2 claims
  313. PATH_EXISTS appliedsearch.ts crates/dbt-docs-server/API-CONTRACTS.md:777-777
     tier: bare
     raw: `SearchResultsContents.tsx` calls **one** GraphQL hook (`useSearchResults` / `GetAppliedSearchResults`) that returns interleaved `models | sources | t
  314. PATH_EXISTS searchresultscontents.tsx crates/dbt-docs-server/API-CONTRACTS.md:777-777
     tier: bare
     raw: `SearchResultsContents.tsx` calls **one** GraphQL hook (`useSearchResults` / `GetAppliedSearchResults`) that returns interleaved `models | sources | t
  315. PATH_EXISTS src/hooks/discovery/source.ts crates/dbt-docs-server/API-CONTRACTS.md:844-844
     tier: unanchored
     raw: GraphQL hooks: `packages/metadata/dbt-explorer/src/hooks/dbtStrategy/useSource.ts` → `src/hooks/discovery/source.ts` (`GetSourceByUniqueId`)
  316. SYMBOL_EXISTS dbt.catalog_tables crates/dbt-docs-server/API-CONTRACTS.md:968-968
     tier: -
     raw: Notes Column names constituting the PK; empty array if none. Sourced from `dbt.nodes.primary_key` (a `List<String>` column) — not from `dbt.catalog_ta
     cited by 8 claims
  317. SYMBOL_EXISTS dbt.nodes.primary_key crates/dbt-docs-server/API-CONTRACTS.md:968-968
     tier: -
     raw: Notes Column names constituting the PK; empty array if none. Sourced from `dbt.nodes.primary_key` (a `List<String>` column) — not from `dbt.catalog_ta
     cited by 2 claims
  318. SYMBOL_EXISTS dbt.source_freshness.parquet crates/dbt-docs-server/API-CONTRACTS.md:1071-1071
     tier: -
     raw: Freshness parquet coexistence is unverified.** `dbt.source_freshness.parquet`
     cited by 2 claims
  319. SYMBOL_EXISTS dbt.nodes.parquet crates/dbt-docs-server/API-CONTRACTS.md:1073-1073
     tier: -
     raw: freshness`) from the one that writes `dbt.nodes.parquet` (`dbt build` / `dbt parse`).
     cited by 13 claims
  320. PATH_EXISTS feature-to-endpoint-mapping.md crates/dbt-docs-server/API-CONTRACTS.md:1074-1074
     tier: bare
     raw: The question from FEATURE-TO-ENDPOINT-MAPPING.md Appendix B1: does `dbt --use-index
     cited by 7 claims
  321. SYMBOL_EXISTS dbt.source_freshness crates/dbt-docs-server/API-CONTRACTS.md:1078-1078
     tier: -
     raw: before relying on `dbt.source_freshness` as the freshness data source.
     cited by 3 claims
  322. SYMBOL_EXISTS dbt.nodes.alias crates/dbt-docs-server/API-CONTRACTS.md:1110-1110
     tier: -
     raw: `dbt.nodes.alias` for seeds (the field that overrides the CSV filename to set the
     cited by 2 claims
  323. PATH_EXISTS src/hooks/dbtstrategy/usesnapshot.ts crates/dbt-docs-server/API-CONTRACTS.md:1335-1335
     tier: unanchored
     raw: GraphQL hooks: `packages/metadata/dbt-explorer/src/hooks/discovery/snapshot.ts` (`GetSnapshotByUniqueId`) and `src/hooks/dbtStrategy/useSnapshot.ts`
  324. PATH_EXISTS snapshotview.tsx crates/dbt-docs-server/API-CONTRACTS.md:1539-1539
     tier: bare
     raw: `patch_path` presence in parquet is unverified.** `SnapshotView.tsx` reads
  325. PATH_EXISTS src/hooks/discovery/test.ts crates/dbt-docs-server/API-CONTRACTS.md:1578-1578
     tier: unanchored
     raw: GraphQL hook: `packages/metadata/dbt-explorer/src/hooks/dbtStrategy/useTest.ts` → `src/hooks/discovery/test.ts` (`GetTestByUniqueId`)
  326. SYMBOL_EXISTS dbt.edges crates/dbt-docs-server/API-CONTRACTS.md:1690-1690
     tier: -
     raw: Notes 1-hop upstream from `dbt.edges` parquet; maps to `parents` in GraphQL
     cited by 15 claims
  327. SYMBOL_EXISTS dbt.test_metadata crates/dbt-docs-server/API-CONTRACTS.md:1792-1792
     tier: -
     raw: `description`) with `dbt.test_metadata` (for `column_name`, `severity`, `kwargs`,
     cited by 3 claims
  328. SYMBOL_EXISTS dbt.unit_tests.parquet crates/dbt-docs-server/API-CONTRACTS.md:1798-1798
     tier: -
     raw: `dbt.unit_tests.parquet`. The handler must detect `resource_type = 'unit_test'` from
     cited by 4 claims
  329. PATH_EXISTS src/hooks/discovery/exposure.ts crates/dbt-docs-server/API-CONTRACTS.md:1856-1856
     tier: unanchored
     raw: GraphQL hooks: `packages/metadata/dbt-explorer/src/hooks/dbtStrategy/useExposure.ts` → `src/hooks/discovery/exposure.ts` (`GetExposureByUniqueId`)
  330. SYMBOL_EXISTS dbt.exposures.parquet crates/dbt-docs-server/API-CONTRACTS.md:1863-1863
     tier: -
     raw: parquet table — `dbt.exposures.parquet` — not in `dbt.nodes` (schema confirmed in
     cited by 14 claims
  331. SYMBOL_EXISTS dbt.exposures.created_at crates/dbt-docs-server/API-CONTRACTS.md:1905-1905
     tier: -
     raw: `dbt.exposures.created_at`).
     cited by 2 claims
  332. SYMBOL_EXISTS dbt.exposures.tags crates/dbt-docs-server/API-CONTRACTS.md:1920-1920
     tier: -
     raw: Notes From `dbt.exposures.tags` (list_utf8 column)
     cited by 2 claims
  333. SYMBOL_EXISTS dbt.exposures.fqn crates/dbt-docs-server/API-CONTRACTS.md:1921-1921
     tier: -
     raw: Notes From `dbt.exposures.fqn` (list_utf8 column)
  334. SYMBOL_EXISTS dbt.exposures.depends_on_nodes crates/dbt-docs-server/API-CONTRACTS.md:1929-1929
     tier: -
     raw: Notes 1-hop upstream models + sources; derived from `dbt.exposures.depends_on_nodes` — see Risk #4
     cited by 5 claims
  335. SYMBOL_EXISTS dbt.exposures.ingested_at crates/dbt-docs-server/API-CONTRACTS.md:1934-1934
     tier: -
     raw: Notes Class B: environment-level field on the GraphQL `applied` wrapper, not on the exposure row; ingest timestamp lives in `dbt.exposures.ingested_at
  336. PATH_EXISTS exposureview.tsx crates/dbt-docs-server/API-CONTRACTS.md:1994-1994
     tier: bare
     raw: `file_path` vs. `original_file_path` for the header file list.** `ExposureView.tsx`
  337. PATH_EXISTS exposurestatustilesection.tsx crates/dbt-docs-server/API-CONTRACTS.md:2007-2007
     tier: bare
     raw: FE engineers do not silently fall through unknown strings. `ExposureStatusTileSection.tsx`
     cited by 2 claims
  338. SYMBOL_EXISTS dbt.exposures.depends_on_macros crates/dbt-docs-server/API-CONTRACTS.md:2021-2021
     tier: -
     raw: prefix is faster and matches what `ExposureRow` already encodes. `dbt.exposures.depends_on_macros`
  339. PATH_EXISTS web/src/api.ts crates/dbt-docs-server/API-CONTRACTS.md:2054-2054
     tier: unanchored
     raw: `web/src/api.ts`.
     cited by 4 claims
  340. SYMBOL_EXISTS dbt.groups.ingested_at crates/dbt-docs-server/API-CONTRACTS.md:2160-2160
     tier: -
     raw: column in parquet, so `dbt.groups.ingested_at` (ISO 8601) is the fallback.
  341. SYMBOL_EXISTS dbt.groups.parquet crates/dbt-docs-server/API-CONTRACTS.md:2182-2182
     tier: -
     raw: Notes Empirically confirmed: NOT a top-level column in `dbt.groups.parquet` (schema is `unique_id, name, description, package_name, file_path, origina
     cited by 6 claims
  342. SYMBOL_EXISTS dbt.nodes.unique_id crates/dbt-docs-server/API-CONTRACTS.md:2190-2190
     tier: -
     raw: Notes From `dbt.nodes.unique_id`
  343. SYMBOL_EXISTS dbt.macros.depends_on_macros crates/dbt-docs-server/API-CONTRACTS.md:2338-2338
     tier: -
     raw: `depends_on` from this macro's own `dbt.macros.depends_on_macros` list column;
     cited by 2 claims
  344. SYMBOL_EXISTS dbt.nodes.depends_on_macros crates/dbt-docs-server/API-CONTRACTS.md:2339-2339
     tier: -
     raw: `referenced_by` from inverse scans of `dbt.nodes.depends_on_macros` (and other
  345. SYMBOL_EXISTS dbt.macros.created_at crates/dbt-docs-server/API-CONTRACTS.md:2411-2411
     tier: -
     raw: per ADR-5 (epoch seconds, sourced from `dbt.macros.created_at`).
  346. SYMBOL_EXISTS dbt.macros.docs_show crates/dbt-docs-server/API-CONTRACTS.md:2431-2431
     tier: -
     raw: Notes From `dbt.macros.docs_show`; whether the macro should appear in generated docs. FE may use this to hide internal helpers — currently the dbt-ui 
  347. SYMBOL_EXISTS dbt.macros.arguments crates/dbt-docs-server/API-CONTRACTS.md:2433-2433
     tier: -
     raw: Notes From `dbt.macros.arguments` (stored as JSON string — `Option<String>`). Handler must `json_extract` and re-serialize as a list of `{name, type, 
     cited by 4 claims
  348. SYMBOL_EXISTS dbt.nodes crates/dbt-docs-server/API-CONTRACTS.md:2497-2497
     tier: -
     raw: No handler exists yet; SELECT must target `dbt.macros`, not `dbt.nodes`.** Every other
     evidence: field:dbt.artifacts.schemas.manifest.Manifest.nodes:crates/dbt-sa-python/python/dbt/artifacts/schemas/manifest.py:34
     cited by 2 claims
  349. PATH_EXISTS src/handlers/macros.rs crates/dbt-docs-server/API-CONTRACTS.md:2501-2501
     tier: unanchored
     raw: needs its own handler file (`src/handlers/macros.rs`) with its own SELECT. `NodeBase`
     cited by 2 claims
  350. SYMBOL_EXISTS dbt.macros.parquet crates/dbt-docs-server/API-CONTRACTS.md:2512-2512
     tier: -
     raw: Empirically confirmed against `dbt.macros.parquet` (671 rows in the sample project):
     cited by 6 claims
  351. SYMBOL_EXISTS dbt.metrics.parquet crates/dbt-docs-server/API-CONTRACTS.md:2570-2570
     tier: -
     raw: `type_params` is a JSON blob, not a discriminated union.** The `dbt.metrics.parquet`
     cited by 14 claims
  352. PATH_EXISTS crates/dbt-index/src/parquet.rs crates/dbt-docs-server/API-CONTRACTS.md:2584-2584
     tier: anchored
     raw: `crates/dbt-index/src/parquet.rs` has no `formula` column — only `metric_filter`
     cited by 4 claims
  353. PATH_EXISTS src/hooks/discovery/metric.ts crates/dbt-docs-server/API-CONTRACTS.md:2611-2611
     tier: unanchored
     raw: GraphQL hook: `packages/metadata/dbt-explorer/src/hooks/dbtStrategy/useMetric.ts` → `src/hooks/discovery/metric.ts` (`GetMetricByUniqueId`)
  354. SYMBOL_EXISTS dbt.metrics.created_at crates/dbt-docs-server/API-CONTRACTS.md:2667-2667
     tier: -
     raw: (epoch seconds, sourced from `dbt.metrics.created_at`).
  355. SYMBOL_EXISTS dbt.metrics.fqn crates/dbt-docs-server/API-CONTRACTS.md:2683-2683
     tier: -
     raw: Notes From `dbt.metrics.fqn`; rendered in GeneralView LineageSection
  356. SYMBOL_EXISTS dbt.metrics.tags crates/dbt-docs-server/API-CONTRACTS.md:2684-2684
     tier: -
     raw: Notes From `dbt.metrics.tags`
     cited by 2 claims
  357. SYMBOL_EXISTS dbt.metrics.input_metric_names crates/dbt-docs-server/API-CONTRACTS.md:2690-2690
     tier: -
     raw: Notes Names of input metrics for `ratio` (numerator/denominator) and `derived` (metrics[]) types; from `dbt.metrics.input_metric_names` (denormalized 
     cited by 2 claims
  358. SYMBOL_EXISTS dbt.metrics.ai_context crates/dbt-docs-server/API-CONTRACTS.md:2715-2715
     tier: -
     raw: Notes `dbt.metrics.ai_context` exists but is Proprietary/dbt-v2-specific; not a Discovery-public field. Defer until a UI consumer exists
     cited by 2 claims
  359. SYMBOL_EXISTS dbt.metrics.config crates/dbt-docs-server/API-CONTRACTS.md:2716-2716
     tier: -
     raw: Notes `dbt.metrics.config` JSON exists but has no Discovery-public schema; defer until a UI consumer exists. Mirrors `TestDetail` Risk: the GraphQL `c
     cited by 2 claims
  360. SYMBOL_EXISTS dbt.metrics.refs crates/dbt-docs-server/API-CONTRACTS.md:2717-2717
     tier: -
     raw: Notes `dbt.metrics.refs` JSON exists but is denormalized into `depends_on` via `dbt.edges`; do not duplicate
  361. PATH_EXISTS metricfiltertable.tsx crates/dbt-docs-server/API-CONTRACTS.md:2771-2771
     tier: bare
     raw: `filter` shape divergence between manifest and renderer — [DECIDED: our contract follows manifest/parquet truth].** The dbt-ui Zod schema in `discover
  362. SYMBOL_EXISTS dbt.metrics.metric_filter crates/dbt-docs-server/API-CONTRACTS.md:2771-2771
     tier: -
     raw: The manifest v10 shape (which `dbt.metrics.metric_filter` mirrors via `jjson(m, "filter")`) has `{ where_filters: [{ where_sql_template }] }`.
     cited by 2 claims
  363. PATH_EXISTS semantic_manifest.json crates/dbt-docs-server/API-CONTRACTS.md:2799-2799
     tier: bare
     raw: tables are emitted today by any project with a `semantic_manifest.json`, regardless
     cited by 2 claims
  364. SYMBOL_EXISTS dbt.saved_queries.created_at crates/dbt-docs-server/API-CONTRACTS.md:2845-2845
     tier: -
     raw: (parquet-backed; epoch seconds in `dbt.saved_queries.created_at`).
  365. PATH_EXISTS src/hooks/dbtstrategy/usesavedquery.ts crates/dbt-docs-server/API-CONTRACTS.md:2853-2853
     tier: unanchored
     raw: GraphQL hook: `packages/metadata/dbt-explorer/src/hooks/discovery/savedQuery.ts` (`GetSavedQueryByUniqueId`) and `src/hooks/dbtStrategy/useSavedQuery.
  366. SYMBOL_EXISTS dbt.saved_queries.parquet crates/dbt-docs-server/API-CONTRACTS.md:2859-2859
     tier: -
     raw: `dbt.saved_queries.parquet` (see `SavedQueryRow` in `crates/dbt-index/src/parquet.rs`),
     cited by 5 claims
  367. SYMBOL_EXISTS dbt.saved_queries.fqn crates/dbt-docs-server/API-CONTRACTS.md:2936-2936
     tier: -
     raw: Notes from `dbt.saved_queries.fqn`
  368. SYMBOL_EXISTS dbt.saved_queries.tags crates/dbt-docs-server/API-CONTRACTS.md:2937-2937
     tier: -
     raw: Notes from `dbt.saved_queries.tags`
     cited by 4 claims
  369. SYMBOL_EXISTS dbt.saved_queries.exports crates/dbt-docs-server/API-CONTRACTS.md:2948-2948
     tier: -
     raw: Notes Parsed from JSON-string column `dbt.saved_queries.exports`; empty array if no exports defined
  370. SYMBOL_EXISTS dbt.edges.parquet crates/dbt-docs-server/API-CONTRACTS.md:3065-3065
     tier: -
     raw: theoretically be referenced by an `exposure`. Verify `dbt.edges.parquet` records
  371. PATH_EXISTS crates/dbt-index/src/ingest/semantic_manifest.rs crates/dbt-docs-server/API-CONTRACTS.md:3104-3104
     tier: anchored
     raw: Their parquet source (`dbt.semantic_models` + `dbt.semantic_{entities,measures,dimensions}`) is written by `dbt parse` / `dbt build` during semantic-m
  372. PATH_EXISTS src/hooks/discovery/semanticmodel.ts crates/dbt-docs-server/API-CONTRACTS.md:3115-3115
     tier: unanchored
     raw: GraphQL hooks: `packages/metadata/dbt-explorer/src/hooks/dbtStrategy/useSemanticModel.ts` → `src/hooks/discovery/semanticModel.ts` (`GetSemanticModelB
  373. SYMBOL_EXISTS dbt.semantic_dimensions crates/dbt-docs-server/API-CONTRACTS.md:3117-3117
     tier: -
     raw: Their parquet source is the `dbt.semantic_models` table (one row per semantic model) plus three sibling tables joined on the parent `unique_id`: `dbt.
     cited by 4 claims
  374. SYMBOL_EXISTS dbt.semantic_entities crates/dbt-docs-server/API-CONTRACTS.md:3117-3117
     tier: -
     raw: Their parquet source is the `dbt.semantic_models` table (one row per semantic model) plus three sibling tables joined on the parent `unique_id`: `dbt.
     cited by 10 claims
  375. SYMBOL_EXISTS dbt.semantic_measures crates/dbt-docs-server/API-CONTRACTS.md:3117-3117
     tier: -
     raw: Their parquet source is the `dbt.semantic_models` table (one row per semantic model) plus three sibling tables joined on the parent `unique_id`: `dbt.
     cited by 4 claims
  376. SYMBOL_EXISTS dbt.semantic_models.model crates/dbt-docs-server/API-CONTRACTS.md:3117-3117
     tier: -
     raw: The upstream relation is the model the semantic model is built on (the `model:` reference in YAML, captured as `dbt.semantic_models.model` and as a si
     cited by 4 claims
  377. SYMBOL_EXISTS dbt.semantic_models.created_at crates/dbt-docs-server/API-CONTRACTS.md:3221-3221
     tier: -
     raw: (epoch seconds, sourced from `dbt.semantic_models.created_at`).
     cited by 2 claims
  378. SYMBOL_EXISTS dbt.semantic_models.parquet crates/dbt-docs-server/API-CONTRACTS.md:3240-3240
     tier: -
     raw: Notes Empirically verified absent at the top-level of `dbt.semantic_models.parquet`. Handler must extract from the `config` JSON column via `json_extr
     cited by 4 claims
  379. SYMBOL_EXISTS dbt.semantic_models.fqn crates/dbt-docs-server/API-CONTRACTS.md:3241-3241
     tier: -
     raw: Notes `dbt.semantic_models.fqn` (3-part: `[pkg, semantic_models, name]`)
  380. SYMBOL_EXISTS dbt.project.last_indexed_at crates/dbt-docs-server/API-CONTRACTS.md:3298-3298
     tier: -
     raw: Notes Cloud-tier run timestamp; dbt-ui header uses it for "Definition updated as of …" — replace with `dbt.project.last_indexed_at` at the project lev
  381. SYMBOL_EXISTS dbt.semantic_dimensions.parquet crates/dbt-docs-server/API-CONTRACTS.md:3387-3387
     tier: -
     raw: Empirically confirmed against `dbt.semantic_dimensions.parquet`: schema is `unique_id, name, dimension_type, description, label, expr, is_partition, t
  382. SYMBOL_EXISTS dbt.semantic_models.primary_entity crates/dbt-docs-server/API-CONTRACTS.md:3393-3393
     tier: -
     raw: `primary_entity` may duplicate one of the `entities[]` rows.** `dbt.semantic_models.primary_entity` stores the name of an entity (often also listed in
  383. SYMBOL_EXISTS dbt.semantic_relationships crates/dbt-docs-server/API-CONTRACTS.md:3397-3397
     tier: -
     raw: `semantic_relationships` is intentionally omitted from v0.** `dbt.semantic_relationships` (parquet schema at `crates/dbt-index/src/parquet.rs:1237`) c
  384. PATH_EXISTS appliedallsources.ts crates/dbt-docs-server/API-CONTRACTS.md:3410-3410
     tier: bare
     raw: FE keeps the aggregation it already does.** `appliedAllSources.ts` already fetches per-table rows and the FilterView already aggregates them client-si
  385. PATH_EXISTS src/handlers/sources.rs crates/dbt-docs-server/API-CONTRACTS.md:3414-3414
     tier: unanchored
     raw: Verified against `~/codaz/sl-schema-evolution/sample_project/target/index/` and the existing `src/handlers/sources.rs` (the DETAIL handler is the auth
     cited by 3 claims
  386. SYMBOL_EXISTS dbt.sources.parquet crates/dbt-docs-server/API-CONTRACTS.md:3416-3416
     tier: -
     raw: `dbt.nodes.parquet` is the **only** parquet for source rows — there is no separate `dbt.sources.parquet`.
  387. PATH_EXISTS sourcecollectionfilterview.tsx crates/dbt-docs-server/API-CONTRACTS.md:3421-3421
     tier: bare
     raw: Three filter dropdowns in `SourceCollectionFilterView.tsx`, all client-side today (GraphQL response is unfiltered):
     cited by 2 claims
  388. SYMBOL_EXISTS dbt.nodes.database_name crates/dbt-docs-server/API-CONTRACTS.md:3465-3465
     tier: -
     raw: Notes OR'd list of exact-match values against `dbt.nodes.database_name`. Case-sensitive.
     cited by 2 claims
  389. SYMBOL_EXISTS dbt.nodes.schema_name crates/dbt-docs-server/API-CONTRACTS.md:3466-3466
     tier: -
     raw: Notes OR'd list of exact-match values against `dbt.nodes.schema_name`. Case-sensitive.
     cited by 2 claims
  390. SYMBOL_EXISTS dbt.nodes.tags crates/dbt-docs-server/API-CONTRACTS.md:3538-3538
     tier: -
     raw: Notes From `dbt.nodes.tags`. Empty array when absent.
     cited by 2 claims
  391. SYMBOL_EXISTS dbt.source_freshness.status crates/dbt-docs-server/API-CONTRACTS.md:3540-3540
     tier: -
     raw: Notes One of `pass` · `warn` · `error` · `runtime_error`. Normalized from `dbt.source_freshness.status` (which stores `"runtime error"` space-separate
     cited by 2 claims
  392. SYMBOL_EXISTS dbt.source_freshness.max_loaded_at_time_ago crates/dbt-docs-server/API-CONTRACTS.md:3548-3548
     tier: -
     raw: Notes The FE computes relative time client-side from `max_loaded_at`; the per-table `dbt.source_freshness.max_loaded_at_time_ago` is staleness-prone (
  393. SYMBOL_EXISTS dbt.nodes.loader crates/dbt-docs-server/API-CONTRACTS.md:3678-3678
     tier: -
     raw: Notes `dbt.nodes.loader` exists but no dropdown in dbt-ui. Add additively if a Loader filter is ever requested.
  394. PATH_EXISTS appliedseeds.ts crates/dbt-docs-server/API-CONTRACTS.md:3757-3757
     tier: bare
     raw: sort controls. The GraphQL hook (`appliedSeeds.ts`) over-fetches considerably
  395. PATH_EXISTS seedfilterview.tsx crates/dbt-docs-server/API-CONTRACTS.md:3760-3760
     tier: bare
     raw: `stats[]`) — but the rendered `TableData` projection in `SeedFilterView.tsx`
     cited by 3 claims
  396. SYMBOL_EXISTS dbt.catalog_stats.parquet crates/dbt-docs-server/API-CONTRACTS.md:3788-3788
     tier: -
     raw: `dbt.catalog_stats.parquet`: zero rows for `seed.%` in the sample
     cited by 2 claims
  397. PATH_EXISTS snapshotfilterview.tsx crates/dbt-docs-server/API-CONTRACTS.md:4005-4005
     tier: bare
     raw: `SnapshotFilterView.tsx` is one of the simplest resource list views in
     cited by 4 claims
  398. PATH_EXISTS appliedsnapshots.ts crates/dbt-docs-server/API-CONTRACTS.md:4008-4008
     tier: bare
     raw: `appliedSnapshots.ts`. There are **no filter dropdowns** and **no
  399. SYMBOL_EXISTS dbt.catalog_tables.parquet crates/dbt-docs-server/API-CONTRACTS.md:4069-4069
     tier: -
     raw: `dbt.catalog_tables.parquet`: schema confirmed via the sources detail
  400. SYMBOL_EXISTS dbt.nodes.materialized crates/dbt-docs-server/API-CONTRACTS.md:4183-4183
     tier: -
     raw: Notes Always `"snapshot"` for this resource type. Included for symmetry with the detail contract and to avoid forcing clients to special-case the reso
  401. SYMBOL_EXISTS dbt.test_metadata.attached_node crates/dbt-docs-server/API-CONTRACTS.md:4399-4399
     tier: -
     raw: The parquet shape is asymmetric: `dbt.test_metadata.attached_node` carries the tested model's `unique_id` for data tests, but `dbt.unit_tests` stores 
     cited by 2 claims
  402. SYMBOL_EXISTS dbt.test_metadata.parquet crates/dbt-docs-server/API-CONTRACTS.md:4407-4407
     tier: -
     raw: `dbt.test_metadata.parquet`: 20 rows; one-to-one with `nodes.resource_type = 'test'`.
  403. SYMBOL_EXISTS dbt.test_metadata.kwargs crates/dbt-docs-server/API-CONTRACTS.md:4538-4538
     tier: -
     raw: Notes **data test only** — unstructured JSON, deserialized handler-side via CC-7 `json_parse_or_null`. From `dbt.test_metadata.kwargs` (a JSON string 
  404. SYMBOL_EXISTS dbt.test_metadata.severity crates/dbt-docs-server/API-CONTRACTS.md:4616-4616
     tier: -
     raw: `severity` is `string` in parquet but empirically `null` in the sample.** The `dbt.test_metadata.severity` column type is confirmed `string`, but all 
     cited by 2 claims
  405. PATH_EXISTS resourceconstants.ts crates/dbt-docs-server/API-CONTRACTS.md:4675-4675
     tier: bare
     raw: Notes Six values from `testStatusesPlusUnknown` (dbt-dag `resourceConstants.ts`): `pass`, `fail`, `warn`, `error`, `skipped`, `unknown`. Server consta
     cited by 4 claims
  406. SYMBOL_EXISTS dbt.exposures.owner_name crates/dbt-docs-server/API-CONTRACTS.md:4750-4750
     tier: -
     raw: handler validates exact match against `dbt.exposures.owner_name` (`= '<value>'`,
     cited by 5 claims
  407. SYMBOL_EXISTS dbt.groups crates/dbt-docs-server/API-CONTRACTS.md:5002-5002
     tier: -
     raw: Notes Distinct non-null `dbt.exposures.owner_name` values, sorted ascending. Sourced from `dbt.exposures` (NOT `dbt.groups`) because exposure owners a
     evidence: field:dbt.artifacts.schemas.manifest.Manifest.groups:crates/dbt-sa-python/python/dbt/artifacts/schemas/manifest.py:49
     cited by 2 claims
  408. PATH_EXISTS definitiongroups.ts crates/dbt-docs-server/API-CONTRACTS.md:5085-5085
     tier: bare
     raw: `useGroupsByIds` in `definitionGroups.ts` takes a `uniqueIds: string[]`
  409. SYMBOL_EXISTS dbt.groups.config crates/dbt-docs-server/API-CONTRACTS.md:5205-5205
     tier: -
     raw: against the `dbt.groups.config` JSON column (verified empirically: the
  410. SYMBOL_EXISTS dbt.nodes.group_name crates/dbt-docs-server/API-CONTRACTS.md:5289-5289
     tier: -
     raw: way, the JOIN must be scoped by `package_name` AND `name` — `dbt.nodes.group_name`
  411. PATH_EXISTS models.rs crates/dbt-docs-server/API-CONTRACTS.md:5517-5517
     tier: bare
     raw: Confirm the filter handler short-circuits on `Some("")` the same way `build_list_sql` in `models.rs` already does for its filters (`.filter(|s| !s.is_
  412. SYMBOL_EXISTS dbt.macros.package_name crates/dbt-docs-server/API-CONTRACTS.md:5561-5561
     tier: -
     raw: Notes Distinct package names from `dbt.macros.package_name`, sorted ascending. See Risk #2 for the `dbt.packages` join decision.
  413. PATH_EXISTS src/handlers/models.rs crates/dbt-docs-server/API-CONTRACTS.md:5583-5583
     tier: unanchored
     raw: The handler should follow the `list_model_facets` pattern in `src/handlers/models.rs` (spawn-blocking + `query_arrow` + `batches_to_*_names` extractor
     cited by 5 claims
  414. SYMBOL_EXISTS dbt.metrics.meta crates/dbt-docs-server/API-CONTRACTS.md:5703-5703
     tier: -
     raw: Notes Available on the detail endpoint. JSON-string per CC-7 (`dbt.metrics.meta` is `Option<String>`). Omitted from the list row to keep the row small
  415. PATH_EXISTS src/handlers/metrics.rs crates/dbt-docs-server/API-CONTRACTS.md:5753-5753
     tier: unanchored
     raw: A new `MetricListResponse` / `MetricSummary` struct lives in `src/handlers/metrics.rs` (net-new file alongside the metrics detail handler, parallel to
  416. SYMBOL_EXISTS dbt.metrics.package_name crates/dbt-docs-server/API-CONTRACTS.md:5810-5810
     tier: -
     raw: Notes Reserved for a future revision that adds a `?package=` filter (parallel to `GET /api/v1/macros/facets.packages`). Distinct values from `dbt.metr
  417. SYMBOL_EXISTS dbt.metrics.group_name crates/dbt-docs-server/API-CONTRACTS.md:5811-5811
     tier: -
     raw: Notes Reserved for a future revision that adds a `?owner=` (= `group_name`) filter. Distinct values from `dbt.metrics.group_name` (skip nulls).
  418. SYMBOL_EXISTS dbt.saved_queries.depends_on_nodes crates/dbt-docs-server/API-CONTRACTS.md:5926-5926
     tier: -
     raw: Notes Truncatable per CC-6. From `dbt.saved_queries.depends_on_nodes` (`[list_utf8!]`). Typically references `metric.*` / `semantic_model.*` unique_id
  419. SYMBOL_EXISTS dbt.saved_queries.refs crates/dbt-docs-server/API-CONTRACTS.md:5932-5932
     tier: -
     raw: Notes `dbt.saved_queries.refs` is an internal serialized representation of YAML `ref()` calls; the resolved `depends_on_nodes[]` is the canonical surf
  420. PATH_EXISTS src/handlers/saved_queries.rs crates/dbt-docs-server/API-CONTRACTS.md:5969-5969
     tier: unanchored
     raw: The handler should follow the `list_models` pattern in `src/handlers/models.rs` (spawn-blocking + `query_arrow` + `batches_to_*_rows` extractor) and l
  421. PATH_EXISTS savedqueryfilterview.tsx crates/dbt-docs-server/API-CONTRACTS.md:5983-5983
     tier: bare
     raw: GraphQL `filter` is unused by the dbt-ui view.** `useDiscoveryDefinitionSavedQueries` accepts a `filter: GenericMaterializedFilter` argument; `SavedQu
  422. SYMBOL_EXISTS dbt.saved_queries.package_name crates/dbt-docs-server/API-CONTRACTS.md:6023-6023
     tier: -
     raw: Notes No package facet — `SavedQueryFilterView` does not render a `PackageFilterDropdown`. The parquet column `dbt.saved_queries.package_name` is pres
  423. SYMBOL_EXISTS dbt.saved_queries.group_name crates/dbt-docs-server/API-CONTRACTS.md:6025-6025
     tier: -
     raw: Notes No owners facet — `SavedQueryFilterView` does not render an Owner dropdown. The parquet `dbt.saved_queries.group_name` is available for a future
  424. PATH_EXISTS definitionsemanticmodels.ts crates/dbt-docs-server/API-CONTRACTS.md:6058-6058
     tier: bare
     raw: The corresponding GraphQL hook (`definitionSemanticModels.ts`) fetches `entities { name, type }` as a nested object array on each `SemanticModelDefini
  425. PATH_EXISTS crates/dbt-docs-server/src/handlers/models.rs crates/dbt-docs-server/API-CONTRACTS.md:6195-6195
     tier: anchored
     raw: No existing LIST handler — greenfield endpoint.** The `/api/v1/models` handler (`crates/dbt-docs-server/src/handlers/models.rs`) is the structural tem
  426. PATH_EXISTS src/handlers/nodes.rs crates/dbt-docs-server/API-CONTRACTS.md:6260-6260
     tier: unanchored
     raw: Reference `src/handlers/models.rs` for the list/sort/cursor pattern and `src/handlers/nodes.rs` for cross-resource aggregation over `dbt.nodes`.
  427. SYMBOL_EXISTS dbt.nodes.original_file_path crates/dbt-docs-server/API-CONTRACTS.md:6272-6272
     tier: -
     raw: Notes Comma-separated modeling-layer filter. Mirrors `/api/v1/models?modeling_layer=`. Allowed values: `Staging`, `Intermediate`, `Marts`. Multiple va
  428. PATH_EXISTS searchpage.tsx crates/dbt-docs-server/API-CONTRACTS.md:6290-6290
     tier: bare
     raw: Non-goal — `/api/v1/search/facets`.** `SearchPage.tsx` mounts `ResourceFilterPanel` from `src/components/ResourceFilterPanel/`, which is fed by the ex
  429. PATH_EXISTS src/components/resourcefilterpanel/ crates/dbt-docs-server/API-CONTRACTS.md:6290-6290
     tier: unanchored
     raw: Non-goal — `/api/v1/search/facets`.** `SearchPage.tsx` mounts `ResourceFilterPanel` from `src/components/ResourceFilterPanel/`, which is fed by the ex
  430. PATH_EXISTS util/input.ts crates/dbt-docs-server/API-CONTRACTS.md:6296-6296
     tier: unanchored
     raw: When `len(q) > 1024`. Matches the `MAXIMUM_QUERY_LENGTH` constant in dbt-ui `util/input.ts`. The 1024-char cap protects the SQL planner from pathologi
  431. SYMBOL_EXISTS dbt.nodes.description crates/dbt-docs-server/API-CONTRACTS.md:6733-6733
     tier: -
     raw: `highlight` shape 80-char window centered on the first match in `dbt.nodes.description` (or the corresponding column on `dbt.exposures`, `dbt.macros`,
     cited by 3 claims
  432. SYMBOL_EXISTS dbt.node_columns.column_name crates/dbt-docs-server/API-CONTRACTS.md:6735-6735
     tier: -
     raw: `highlight` shape Comma-and-space-joined string (`"col_a, col_b"`) of all column names within this resource that match the query, each with the matche
  433. PATH_EXISTS filterprovider.tsx crates/dbt-docs-server/API-CONTRACTS.md:6747-6747
     tier: bare
     raw: Why excluded ❌ Deferred. `SearchFieldType` GraphQL enum has `columnDescription` as a distinct value, but the UI's `allSearchTypes` (`FilterProvider.ts
  434. SYMBOL_EXISTS dbt.docs.parquet crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: `dbt.docs.parquet` is the doc-block table (for `{{ doc() }}` references), not per-node descriptions.
  435. SYMBOL_EXISTS dbt.docs crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Description searches scan `dbt.nodes.description` directly — no `dbt.docs` join required.** The parquet sample shows `dbt.nodes.description` is popula
     evidence: field:dbt.artifacts.schemas.manifest.Manifest.docs:crates/dbt-sa-python/python/dbt/artifacts/schemas/manifest.py:38
  436. SYMBOL_EXISTS dbt.exposures.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  437. SYMBOL_EXISTS dbt.groups.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  438. SYMBOL_EXISTS dbt.macros.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  439. SYMBOL_EXISTS dbt.metrics.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  440. SYMBOL_EXISTS dbt.saved_queries.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  441. SYMBOL_EXISTS dbt.semantic_models.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  442. SYMBOL_EXISTS dbt.unit_tests.description crates/dbt-docs-server/API-CONTRACTS.md:6891-6891
     tier: -
     raw: Per-table description columns: `dbt.nodes.description`, `dbt.exposures.description`, `dbt.macros.description`, `dbt.metrics.description`, `dbt.saved_q
  443. PATH_EXISTS vortex_sender.rs crates/dbt-docs-server/API-CONTRACTS.md:6928-6928
     tier: bare
     raw: Two in-repo siblings already emit to Vortex — `crates/dbt-index` (`telemetry.rs` + `vortex_sender.rs`) and `wizard/dbt-codex/codex-rs/vortex` — and bo
  444. PATH_EXISTS protogen.toml crates/dbt-docs-server/API-CONTRACTS.md:6960-6960
     tier: bare
     raw: Con:** heavier — drags in `cargo xtask protogen`, `protogen.toml`, and a `proto-rust`/`vortex-client` dependency; the `docs.*` types only exist after 
     cited by 5 claims
  445. PATH_EXISTS src/handlers/analytics.rs crates/dbt-docs-server/API-CONTRACTS.md:6973-6973
     tier: unanchored
     raw: Hand-rolls the `docs.proto` wire structs in `src/handlers/analytics.rs` and ships a self-contained `src/vortex_sender.rs` (no `proto-rust`, no `vortex
     cited by 2 claims
  446. PATH_EXISTS src/vortex_sender.rs crates/dbt-docs-server/API-CONTRACTS.md:6973-6973
     tier: unanchored
     raw: Hand-rolls the `docs.proto` wire structs in `src/handlers/analytics.rs` and ships a self-contained `src/vortex_sender.rs` (no `proto-rust`, no `vortex
  447. PATH_EXISTS run_results.json crates/dbt-docs-server/README.md:63-63
     tier: bare
     raw: > Publishing `target/` publishes everything in it: `manifest.json`, `run_results.json`,
  448. SYMBOL_EXISTS dbt.column_lineage.parquet crates/dbt-docs-server/README.md:67-67
     tier: -
     raw: Column-level lineage rides along when the index has it, which is what `--static-analysis strict` on the compile or build produces; the site derives wh
  449. PATH_EXISTS web/public/ crates/dbt-docs-server/README.md:244-244
     tier: unanchored
     raw: Favicon** — none is set by default. Add an icon file under `web/public/`
  450. PATH_EXISTS web/ crates/dbt-docs-server/README.md:256-256
     tier: bare
     raw: convention dbt Docs v1 used — no `web/` code changes needed, but it does
     evidence: dir:crates/dbt-docs-server/web/
  451. PATH_EXISTS dbt_cloud.yml crates/dbt-platform-auth/README.md:34-34
     tier: bare
     raw: `CloudYamlResolver`** — `./dbt_cloud.yml`, then `~/.dbt/dbt_cloud.yml`
  452. PATH_EXISTS .agents/vortex-anonymous-telemetry.md crates/dbt-telemetry/README.md:18-18
     tier: anchored
     raw: telemetry is covered by `.agents/vortex-anonymous-telemetry.md`.
     cited by 2 claims
  453. PATH_EXISTS scripts/sync_protos.sh crates/proto-rust/README.md:6-6
     tier: unanchored
     raw: sibling of this repository and run the `./scripts/sync_protos.sh` script to
  454. PATH_EXISTS .gitattributes crates/proto-rust/README.md:53-53
     tier: bare
     raw: regenerate it on every build. `.gitattributes` declares these files are
  455. PATH_EXISTS _includes.rs crates/proto-rust/README.md:58-58
     tier: bare
     raw: We don't rely on auto-generated `_includes.rs` or `mod.rs` files. Instead we

