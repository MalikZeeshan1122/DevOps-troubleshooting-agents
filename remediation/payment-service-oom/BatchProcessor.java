package com.acme.payment;

import java.util.ArrayList;
import java.util.List;

/**
 * Fixed: paginated batch processing to prevent loading all pending
 * transactions into heap (root cause of OOM at line 142).
 */
public class BatchProcessor {

    private static final int DEFAULT_BATCH_SIZE = 500;

    private final TransactionRepository repository;
    private final int batchSize;

    public BatchProcessor(TransactionRepository repository) {
        this(repository, DEFAULT_BATCH_SIZE);
    }

    public BatchProcessor(TransactionRepository repository, int batchSize) {
        this.repository = repository;
        this.batchSize = batchSize;
    }

    public void processPendingTransactions() {
        long lastId = 0L;

        while (true) {
            List<Transaction> batch = repository.fetchPendingBatch(lastId, batchSize);
            if (batch.isEmpty()) {
                break;
            }

            List<Transaction> processed = new ArrayList<>(batch.size());
            for (Transaction tx : batch) {
                processed.add(processTransaction(tx));
            }
            repository.markProcessed(processed);

            lastId = batch.get(batch.size() - 1).getId();
            batch.clear();
            processed.clear();
        }
    }

    private Transaction processTransaction(Transaction tx) {
        // business logic unchanged
        return tx.withStatus(TransactionStatus.PROCESSED);
    }
}
