import React from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Typography
} from '@material-ui/core';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';

import {
  Heading,
  PrimaryButton,
  DisableButton
} from '../materialUI';

import Canvas from '../Canvas';

import { downloadJSON } from '../../utilities/downloadHelper';

import './Home.css';

export default function Workflow({ removeEntity, workflow }) {
  const businessEntityObj = useSelector(state => state.businessEntity);

  const downloadSchema = () => {
    let result = { "transactionWorkflow": [] };
    workflow.map(key => {
      result.transactionWorkflow.push(businessEntityObj[key]);
    });

    downloadJSON("transactionWorkflowModel.json", JSON.stringify(result));
  }

  return <div className="border">
    <div className="heading">
      <Heading text="Transaction Workflow Model" />
      {
        workflow.length === 0 ?
          <DisableButton text="Download JSON" />
          :
          <PrimaryButton onClick={downloadSchema} text="Download JSON" />
      }
    </div>

    <Box
      sx={{
        pt: 2,
        display: 'flex',
        alignItems: 'center'
      }}
    >
      {
        workflow.length > 0 ? <><ArrowDownwardIcon sx={{ color: "red" }} />
          <Typography
            color="textSecondary"
            variant="caption"
          >
            Click on entity to remove from workflow
          </Typography> </> : null
      }
    </Box>
    <Canvas rectDraw={workflow} removeEntity={removeEntity} />
  </div>
}