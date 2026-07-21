'''
有三个训练数据文件，存储在data文件夹中
第一个是experiment.csv 该表格中记录了所有正常实验数据
第二个是missing_columns.csv 该表格中有试验出现数据缺失
第三个是empty.csv 该表格中为值为空
'''

from pathlib import Path
import csv

# 验证文件和表头；逐行解析；收集无效行。
def load_experiments(csv_path):
    valid_records = []
    errors = []
    # required_fields为一个集合，作用为判断csv文件中表头是否齐全
    required_fields = {
        'experiment_name', 
        'train_loss', 
        'val_loss', 
        'accuracy', 
    }
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        # 用要求的字典减去实际的字典
        actual_fields = set(reader.fieldnames or [])
        missing_fields = required_fields - actual_fields

        if missing_fields:
            raise ValueError(
                f'missing required columns: {sorted(missing_fields)}'
            )
        # 将reader转换成一个元素为字典的列表，每一个元素代表一次试验，一个实验包含了四个表头的信息
        rows = list(reader)
        # 把有效记录append到list
        for row in rows:
            if (
                len(row['experiment_name']) > 0
                or not 0 <= float(row['train_loss'].strip()) <= 1
                or not 0 <= float(row['val_loss'].strip()) <= 1
                or not 0 <= float(row['accuracy'].strip()) <= 1
            ):
                valid_records.append(row)
            else:
                errors.append(row)
    return valid_records, errors
    
# 将三个数值字段转换成float
def parse_float(raw_value, field_name, row_numuber):
    
    return float

# 使用max(records, key=...)找出准确率最高的记录
# 使用sum/len计算平均准确率

def main():
    repo_root = Path(__file__).resolve().parents[0]
    csv_path = [repo_root / "data" / "experiments.csv"]

    for csv_path in csv_path:
        valid_records, errors = load_experiments(csv_path)
    print(valid_records, errors)
if __name__ == '__main__':
    main()

# 第一次提交内容：正常路径读取、转换和汇总