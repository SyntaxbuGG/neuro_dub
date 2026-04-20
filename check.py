import torch

print(f"Доступен ли CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Текущая видеокарта: {torch.cuda.get_device_name(0)}")
else:
    print("Увы, работает только CPU.")


print(torch.backends.cudnn.is_available())



