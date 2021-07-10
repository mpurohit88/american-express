import { createStore, applyMiddleware } from 'redux';
import { createLogger } from 'redux-logger';

import transactionWorkflow from './transactionWorkflow/reducer'

const logger = createLogger();

const initialState = { businessEntity: [] };

const store = createStore(transactionWorkflow, initialState, applyMiddleware(logger));

export default store;