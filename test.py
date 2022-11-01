patch = '''
@@ -29,6 +29,7 @@ public static XContentBuilder docMapping() throws IOException {
         XContentBuilder builder = jsonBuilder();
         builder.startObject();
             builder.startObject(TYPE);
+                ElasticsearchMappings.addMetaInformation(builder);
                 ElasticsearchMappings.addDefaultMapping(builder);
                 builder.startObject(ElasticsearchMappings.PROPERTIES)
                     .startObject(Calendar.ID.getPreferredName())
 
@@ -109,10 +109,11 @@ public static void createAnnotationsIndexIfNecessary(Settings settings, Client c
     }
 
     public static XContentBuilder annotationsMapping() throws IOException {
-        return jsonBuilder()
+        XContentBuilder builder = jsonBuilder()
             .startObject()
-                .startObject(ElasticsearchMappings.DOC_TYPE)
-                    .startObject(ElasticsearchMappings.PROPERTIES)
+                .startObject(ElasticsearchMappings.DOC_TYPE);
+        ElasticsearchMappings.addMetaInformation(builder);
+        builder.startObject(ElasticsearchMappings.PROPERTIES)
                         .startObject(Annotation.ANNOTATION.getPreferredName())
                             .field(ElasticsearchMappings.TYPE, ElasticsearchMappings.TEXT)
                         .endObject()
@@ -143,5 +144,6 @@ public static XContentBuilder annotationsMapping() throws IOException {
                     .endObject()
                 .endObject()
             .endObject();
+        return builder;
     }
 }
 
@@ -960,10 +960,10 @@ private static void addModelSizeStatsFieldsToMapping(XContentBuilder builder) th
     }
 
     public static XContentBuilder auditMessageMapping() throws IOException {
-        return jsonBuilder()
-                .startObject()
-                    .startObject(AuditMessage.TYPE.getPreferredName())
-                        .startObject(PROPERTIES)
+        XContentBuilder builder = jsonBuilder().startObject()
+            .startObject(AuditMessage.TYPE.getPreferredName());
+        addMetaInformation(builder);
+        builder.startObject(PROPERTIES)
                             .startObject(Job.ID.getPreferredName())
                                 .field(TYPE, KEYWORD)
                             .endObject()
@@ -987,6 +987,7 @@ public static XContentBuilder auditMessageMapping() throws IOException {
                         .endObject()
                     .endObject()
                 .endObject();
+        return builder;
     }
 
     static String[] mappingRequiresUpdate(ClusterState state, String[] concreteIndices, Version minVersion) throws IOException {
 
@@ -18,6 +18,8 @@
  */
 package org.elasticsearch.action.admin.indices.close;
 
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
 import org.elasticsearch.action.ActionListener;
 import org.elasticsearch.action.admin.indices.flush.FlushRequest;
 import org.elasticsearch.action.support.ActionFilters;
@@ -50,6 +52,7 @@ public class TransportVerifyShardBeforeCloseAction extends TransportReplicationA
     TransportVerifyShardBeforeCloseAction.ShardRequest, TransportVerifyShardBeforeCloseAction.ShardRequest, ReplicationResponse> {
 
     public static final String NAME = CloseIndexAction.NAME + "[s]";
+    protected Logger logger = LogManager.getLogger(getClass());
 
     @Inject
     public TransportVerifyShardBeforeCloseAction(final Settings settings, final TransportService transportService,
@@ -111,8 +114,10 @@ private void executeShardOperation(final ShardRequest request, final IndexShard
             throw new IllegalStateException("Global checkpoint [" + indexShard.getGlobalCheckpoint()
                 + "] mismatches maximum sequence number [" + maxSeqNo + "] on index shard " + shardId);
         }
-        indexShard.flush(new FlushRequest());
-        logger.debug("{} shard is ready for closing", shardId);
+
+        final boolean forced = indexShard.isSyncNeeded();
+        indexShard.flush(new FlushRequest().force(forced));
+        logger.trace("{} shard is ready for closing [forced:{}]", shardId, forced);
     }
 
     @Override
 
@@ -8,6 +8,7 @@
 import org.elasticsearch.action.ActionListener;
 import org.elasticsearch.action.admin.cluster.state.ClusterStateResponse;
 import org.elasticsearch.action.admin.indices.stats.IndicesStatsResponse;
+import org.elasticsearch.action.delete.DeleteResponse;
 import org.elasticsearch.action.search.SearchResponse;
 import org.elasticsearch.action.search.SearchType;
 import org.elasticsearch.action.support.IndicesOptions;
@@ -26,6 +27,7 @@
 import org.elasticsearch.index.shard.IndexShardTestCase;
 import org.elasticsearch.indices.IndicesService;
 import org.elasticsearch.plugins.Plugin;
+import org.elasticsearch.rest.RestStatus;
 import org.elasticsearch.search.SearchService;
 import org.elasticsearch.search.builder.SearchSourceBuilder;
 import org.elasticsearch.search.internal.AliasFilter;
@@ -46,6 +48,8 @@
 import static org.elasticsearch.test.hamcrest.ElasticsearchAssertions.assertAcked;
 import static org.elasticsearch.test.hamcrest.ElasticsearchAssertions.assertHitCount;
 import static org.hamcrest.Matchers.equalTo;
+import static org.hamcrest.Matchers.greaterThanOrEqualTo;
+import static org.hamcrest.Matchers.is;
 
 public class FrozenIndexTests extends ESSingleNodeTestCase {
 
@@ -340,4 +344,30 @@ public void testFreezeIndexIncreasesIndexSettingsVersion() throws ExecutionExcep
         assertThat(client().admin().cluster().prepareState().get().getState().metaData().index(index).getSettingsVersion(),
             equalTo(settingsVersion + 1));
     }
+
+    public void testFreezeEmptyIndexWithTranslogOps() throws Exception {
+        final String indexName = "empty";
+        createIndex(indexName, Settings.builder()
+            .put("index.number_of_shards", 1)
+            .put("index.number_of_replicas", 0)
+            .put("index.refresh_interval", TimeValue.MINUS_ONE)
+            .build());
+
+        final long nbNoOps = randomIntBetween(1, 10);
+        for (long i = 0; i < nbNoOps; i++) {
+            final DeleteResponse deleteResponse = client().prepareDelete(indexName, "_doc", Long.toString(i)).get();
+            assertThat(deleteResponse.status(), is(RestStatus.NOT_FOUND));
+        }
+
+        final IndicesService indicesService = getInstanceFromNode(IndicesService.class);
+        assertBusy(() -> {
+            final Index index = client().admin().cluster().prepareState().get().getState().metaData().index(indexName).getIndex();
+            final IndexService indexService = indicesService.indexService(index);
+            assertThat(indexService.hasShard(0), is(true));
+            assertThat(indexService.getShard(0).getGlobalCheckpoint(), greaterThanOrEqualTo(nbNoOps - 1L));
+        });
+
+        assertAcked(new XPackClient(client()).freeze(new TransportFreezeIndexAction.FreezeRequest(indexName)));
+        assertIndexFrozen(indexName);
+    }
 }
'''

def extract_changes(patch):
    patch_lines = patch.split('\n')
    changes = []
    plus_lines = ""
    minus_lines = ""
    flag = False
    for line in patch_lines:
        if line.startswith('-'):
            minus_lines += line[1:] + '\n'
            flag = True
        elif line.startswith('+'):
            plus_lines += line[1:] + '\n'
            flag = True
        else:
            if flag:
                changes.append((minus_lines, plus_lines))
                minus_lines = ""
                plus_lines = ""
                flag = False

    if flag:
        changes.append((minus_lines, plus_lines))
        minus_lines = ""
        plus_lines = ""
        flag = False

    return changes

res = extract_changes(patch)

with open('changes.txt', 'w') as f:
    for change in res:
        f.write(change[0] + '')
        f.write(change[1] + '')

print(res[4])

x = 4