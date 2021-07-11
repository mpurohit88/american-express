import React from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Typography
} from '@material-ui/core';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';

import { Heading } from '../materialUI';

import { getObjectKeys } from '../../utilities/objectHelper';

import './BusinessEntity.css';

export default function BusinessEntity({ workflow, addWorkflow }) {
  const businessEntityObj = useSelector(state => state.businessEntity);

  const businessEntities = getObjectKeys(businessEntityObj);

  return <>
    <Heading text="Business Entity" />
    <Box
      sx={{
        pt: 2,
        display: 'flex',
        alignItems: 'center'
      }}
    >
      {
        (workflow.length === businessEntities.length) ? null : <><ArrowDownwardIcon sx={{ color: "red" }} />
          <Typography
            color="textSecondary"
            variant="caption"
          >
            Click on entity to add in workflow
          </Typography> </>
      }
    </Box>
    <ul>
      {
        (businessEntities || []).map((entity, index) => {
          if (workflow.find(element => element === entity)) return null;

          return <li key={index} onClick={() => addWorkflow(entity)}>{entity}</li>
        })
      }
    </ul>

  </>
}