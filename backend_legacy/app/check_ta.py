import pandas as pd
import pandas_ta as ta
df = pd.DataFrame({'close': [1, 2, 3, 4, 5], 'high': [1, 2, 3, 4, 5], 'low': [1, 2, 3, 4, 5]})
print("--- PANDAS TA DIR ---")
print(dir(df.ta))
print("--- END ---")
