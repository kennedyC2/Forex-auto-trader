
# while self.auto_trade:
#     # Check RSI
#     if self.rsi > 0:
#          # Get Current Tick Info
#          info = (mt5.symbol_info(self.pair))._asdict()

#           # Check If Database Has Been Updated And Number Of Existing Orders Are Not Greater Than Required
#           if len(self.H_H) > 0 and len(self.L_L) > 0:
#                if (info["ask"] - self.bot_B["price"] > 0.3 and self.rsi >= 65) or (self.bot_B["price"] - info["ask"] > 0.3 and self.rsi >= 65):
#                     for i in range(1, 6):
#                         # Check HP
#                         if (info["ask"] - (i/10) in self.H_H and not self.bot_S["active"]) or (info["ask"] + (i/10) in self.H_H and not self.bot_S["active"]):
#                             s_a1 = threading.Thread(target=self.auto_T1, args=(
#                                 info["ask"], no_of_trades, pattern,), daemon=False)
#                             s_a1.start()

#                 if (self.bot_S["price"] - info["bid"] > 0.3 and self.rsi <= 35) or (info["bid"] - self.bot_S["price"] > 0.3 and self.rsi <= 35):
#                     for i in range(1, 6):
#                         # Check LP
#                         if (info["bid"] - (i/10) in self.L_L and not self.bot_B["active"]) or (info["bid"] + (i/10) in self.L_L and not self.bot_B["active"]):
#                             s_a2 = threading.Thread(target=self.auto_T2, args=(
#                                 info["bid"], no_of_trades, pattern,), daemon=False)
#                             s_a2.start()
