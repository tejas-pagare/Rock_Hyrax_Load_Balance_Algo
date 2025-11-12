// Core Simulation Logic extracted from user-provided single-file implementation

// --- Entity Creation ---
export const createVM = (vmId, mips) => {
  const p_max = (mips * 0.2) + 150;
  const p_idle = p_max * 0.7;
  return { id: vmId, mips, p_max, p_idle };
};

export const createTask = (taskId, length) => {
  return { id: taskId, length };
};

// --- Algorithm Logic ---

export const getEFTs = (vms, vmLoads, task) => {
  return vms.map((vm, i) => (vmLoads[i] + task.length) / vm.mips);
};

export const getFitnessScores = (vms, vmLoads, task, weights) => {
  const efts = getEFTs(vms, vmLoads, task);
  const energyCosts = vms.map(vm => vm.p_max);

  const minTime = Math.min(...efts);
  const maxTime = Math.max(...efts);
  const minEnergy = Math.min(...energyCosts);
  const maxEnergy = Math.max(...energyCosts);

  const normTime = efts.map(t => (maxTime - minTime) > 0 ? (t - minTime) / (maxTime - minTime) : 0);
  const normEnergy = energyCosts.map(e => (maxEnergy - minEnergy) > 0 ? (e - minEnergy) / (maxEnergy - minEnergy) : 0);

  return normTime.map((nt, i) => (weights.w1 * nt) + (weights.w2 * normEnergy[i]));
};

export const rouletteWheelSelect = (probabilities) => {
  const r = Math.random();
  let cumulativeProb = 0;
  for (let i = 0; i < probabilities.length; i++) {
    cumulativeProb += probabilities[i];
    if (r <= cumulativeProb) {
      return i;
    }
  }
  return probabilities.length - 1; // Fallback
};

// --- Step Functions (Pure) ---

export const runRoundRobinStep = (state, vms, task) => {
  const newState = { ...state, vmLoads: [...state.vmLoads] };
  const chosenVmId = newState.counter % vms.length;
  
  const eft = getEFTs(vms, state.vmLoads, task)[chosenVmId];
  newState.taskLog.push({ response_time: eft });
  
  newState.vmLoads[chosenVmId] += task.length;
  newState.counter += 1;
  const log = `Task ${task.id}: Assigned to VM ${chosenVmId} (RR Cycle)`;
  return { newState, log };
};

export const runRhoStep = (state, vms, task, weights) => {
  const newState = { ...state, vmLoads: [...state.vmLoads] };
  
  // Compute detailed components for inspector
  const efts = getEFTs(vms, state.vmLoads, task);
  const energyCosts = vms.map(vm => vm.p_max);

  const minTime = Math.min(...efts);
  const maxTime = Math.max(...efts);
  const minEnergy = Math.min(...energyCosts);
  const maxEnergy = Math.max(...energyCosts);

  const normTime = efts.map(t => (maxTime - minTime) > 0 ? (t - minTime) / (maxTime - minTime) : 0);
  const normEnergy = energyCosts.map(e => (maxEnergy - minEnergy) > 0 ? (e - minEnergy) / (maxEnergy - minEnergy) : 0);

  const fitnessScores = normTime.map((nt, i) => (weights.w1 * nt) + (weights.w2 * normEnergy[i]));
  const alphaVmId = fitnessScores.indexOf(Math.min(...fitnessScores));
  
  let chosenVmId = -1;
  let logReason = "";
  let decisionPhase = "";
  let r1 = Math.random();
  let r2 = Math.random();
  
  if (r1 < 0.5) { // Phase 1: Exploration
    if (r2 < 0.5) {
      chosenVmId = Math.floor(Math.random() * vms.length);
      decisionPhase = "explore-random";
      logReason = `Explore (Random -> ${chosenVmId})`;
    } else {
      chosenVmId = alphaVmId;
      decisionPhase = "explore-alpha";
      logReason = `Explore (-> Alpha ${alphaVmId})`;
    }
  } else { // Phase 2: Exploitation
    chosenVmId = alphaVmId;
    decisionPhase = "exploit-alpha";
    logReason = `Exploit (Alpha ${alphaVmId})`;
  }
  
  const eft = efts[chosenVmId];
  newState.taskLog.push({ response_time: eft });
  
  newState.vmLoads[chosenVmId] += task.length;
  const log = `Task ${task.id}: Alpha=${alphaVmId}. ${logReason}`;
  
  // Inspector data
  const inspectorData = {
    taskId: task.id,
    logReason: `Alpha=${alphaVmId}. ${logReason}`,
    decision: {
      phase: decisionPhase,
      r1,
      r2,
      text: logReason,
    },
    weights: { ...weights },
    efts,
    energyCosts,
    normTime,
    normEnergy,
    minTime,
    maxTime,
    minEnergy,
    maxEnergy,
    alphaVmId,
    chosenVmId,
    fitnessScores: fitnessScores.map((score, i) => ({
      vmId: i,
      score,
      isAlpha: i === alphaVmId,
      isChosen: i === chosenVmId,
    }))
  };
  
  return { newState, log, inspectorData };
};

export const runAcoStep = (state, vms, task) => {
  const newState = { 
    ...state, 
    vmLoads: [...state.vmLoads], 
    pheromones: [...state.pheromones] 
  };
  
  const efts = getEFTs(vms, state.vmLoads, task);
  const eta = efts.map(e => 1.0 / (e + 1e-6));
  
  const attractions = newState.pheromones.map((tau, i) => 
    Math.pow(tau, state.alpha) * Math.pow(eta[i], state.beta)
  );
  
  const sumAttractions = attractions.reduce((a, b) => a + b, 0);
  const probabilities = attractions.map(a => sumAttractions > 0 ? a / sumAttractions : 1 / vms.length);
  
  const chosenVmId = rouletteWheelSelect(probabilities);
  
  const taskFinishTime = efts[chosenVmId];
  newState.taskLog.push({ response_time: taskFinishTime });
  
  newState.vmLoads[chosenVmId] += task.length;
  
  // Update Pheromones
  newState.pheromones = newState.pheromones.map(p => p * (1 - state.evap_rate));
  const depositAmount = 1.0 / (taskFinishTime + 1e-6);
  newState.pheromones[chosenVmId] += depositAmount;
  
  const log = `Task ${task.id}: Chose VM ${chosenVmId} (Prob: ${probabilities[chosenVmId].toFixed(2)})`;
  return { newState, log };
};

// --- Metrics Calculation (Live) ---

export const calculateLiveMetrics = (balancerState, vms, taskCounter) => {
  const vmFinishTimes = vms.map((vm, i) => balancerState.vmLoads[i] / vm.mips);
  
  const makespan = vmFinishTimes.length > 0 ? Math.max(...vmFinishTimes) : 0;
  
  const avgResponseTime = 
    balancerState.taskLog.length > 0 
    ? balancerState.taskLog.reduce((sum, log) => sum + log.response_time, 0) / balancerState.taskLog.length
    : 0;
    
  const throughput = makespan > 0 ? taskCounter / makespan : 0;
  
  const totalEnergy = vmFinishTimes.reduce((energy, busyTime, i) => {
    const vm = vms[i];
    const idleTime = Math.max(0, makespan - busyTime);
    const energyBusy = vm.p_max * busyTime;
    const energyIdle = vm.p_idle * idleTime;
    return energy + energyBusy + energyIdle;
  }, 0);
  
  return {
    "Makespan (s)": makespan,
    "Avg. Response (s)": avgResponseTime,
    "Throughput (tasks/s)": throughput,
    "Energy (kJ)": totalEnergy / 1000
  };
};

// --- Initial States ---

export const getDefaultParams = () => ({
  NUM_VMS: 20,
  NUM_TASKS: 500,
  VM_MIPS_RANGE: [100, 1000],
  TASK_LENGTH_RANGE: [1000, 50000],
  SIM_SPEED: 50, // ms
  RHO_WEIGHTS: { w1: 0.7, w2: 0.3 },
  ACO_PARAMS: { alpha: 1.0, beta: 2.0, evap_rate: 0.1 }
});

export const getInitialBalancersState = (numVms, acoParams) => ({
  rr: {
    vmLoads: Array(numVms).fill(0),
    taskLog: [],
    counter: 0,
  },
  rho: {
    vmLoads: Array(numVms).fill(0),
    taskLog: [],
  },
  aco: {
    vmLoads: Array(numVms).fill(0),
    taskLog: [],
    pheromones: Array(numVms).fill(1),
    ...acoParams,
  }
});
