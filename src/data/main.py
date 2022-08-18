from src.data import make_dataset, analyze_dataset, split_dataset


def main(config=None):
    dataset = make_dataset.main()
    analyze_dataset.main(dataset)
    split_dataset.main(dataset)


if __name__ == '__main__':
    main()
