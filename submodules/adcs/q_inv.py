def q_inv(qin):
  q = []
  q.append(-1*qin.item(0))
  q.append(-1*qin.item(1))
  q.append(-1*qin.item(2))
  q.append(qin.item(3))
  return q
