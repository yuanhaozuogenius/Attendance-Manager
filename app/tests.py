import app.views

# Create your tests here.
file_path = r"data/原始记录表_20230901_20230930.xlsx"
res = app.views.load_data(file_path)
print("res:", res)
