import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';

import { getBusinessEntity } from './redux/transactionWorkflow/action';

import MainLayout from './components/MainLayout';

import './App.css';

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getBusinessEntity());
  })

  return (
    <>
      <MainLayout />
    </>
  );
}

export default App;