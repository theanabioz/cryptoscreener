export const calculateEMA = (data: number[], period: number): number[] => {
  const k = 2 / (period + 1);
  const emaArray = [data[0]];
  for (let i = 1; i < data.length; i++) {
    emaArray.push(data[i] * k + emaArray[i - 1] * (1 - k));
  }
  return emaArray;
};

export const calculateRSI = (close: number[], period: number = 14): number[] => {
  const rsiArray: number[] = [];
  let avgGain = 0;
  let avgLoss = 0;

  // First avg gain/loss (Simple Moving Average)
  for (let i = 1; i <= period; i++) {
    const change = close[i] - close[i - 1];
    if (change > 0) avgGain += change;
    else avgLoss += Math.abs(change);
  }
  avgGain /= period;
  avgLoss /= period;
  
  rsiArray[period] = 100 - 100 / (1 + avgGain / avgLoss);

  // Wilder's Smoothing for subsequent values
  for (let i = period + 1; i < close.length; i++) {
    const change = close[i] - close[i - 1];
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? Math.abs(change) : 0;

    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;

    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss; // Avoid div by zero
    rsiArray[i] = 100 - 100 / (1 + rs);
  }

  // Fill initial undefined with null or 0? Usually we just return array matched by index
  // But caller should know that first 'period' values are missing.
  return rsiArray;
};

export const calculateMACD = (close: number[], fast: number = 12, slow: number = 26, signal: number = 9) => {
  const emaFast = calculateEMA(close, fast);
  const emaSlow = calculateEMA(close, slow);
  
  const macdLine: number[] = [];
  for(let i=0; i<close.length; i++) {
      macdLine.push(emaFast[i] - emaSlow[i]);
  }
  
  const signalLine = calculateEMA(macdLine, signal);
  const histogram = macdLine.map((val, i) => val - signalLine[i]);
  
  return { macdLine, signalLine, histogram };
};

export const calculateBollinger = (close: number[], period: number = 20, stdDev: number = 2) => {
    const upper: number[] = [];
    const lower: number[] = [];
    const sma: number[] = [];

    for (let i = 0; i < close.length; i++) {
        if (i < period - 1) {
            upper.push(NaN);
            lower.push(NaN);
            sma.push(NaN);
            continue;
        }
        
        const slice = close.slice(i - period + 1, i + 1);
        const sum = slice.reduce((a, b) => a + b, 0);
        const mean = sum / period;
        sma.push(mean);
        
        const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / period;
        const std = Math.sqrt(variance);
        
        upper.push(mean + std * stdDev);
        lower.push(mean - std * stdDev);
    }
    
    return { upper, lower, sma };
};
