
from CollectData import CollectData

data_collection = CollectData()
# data_collection.obtain_data(
#     _1503 = True,
#     _4461 = True,
#     packet = True
# )
data_collection.set_data_point()
for ele in data_collection.all_data_points: print(ele)