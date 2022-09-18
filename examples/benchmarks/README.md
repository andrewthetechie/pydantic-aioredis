# benchmarks

[test_benchmarks.py](./test_benchmarks.py) is an example benchmarking suite for pydantic-aioredis. Its a fairly contrived example, using
models copied from our test suite.

This benchmarking suite serves two purposes. First, you can use it as an example to build your own benchmarking suite for your own models and application. Second, it is useful when developing pydantic-aioredis

## Benchmarking during development

Benchmarking is not run as part of CI, due to its results not really being indicative of much.

For development purposes, if you are making changes that might cause performance changes, you can run the benchmarking suite to test that.

1. Run the benchmarking suite against the master branch

```shell
make run-benchmark
```

2. Make your changes in a branch
3. Run the benchmark again against your branch

```shell
make run-benchmark
test_benchmarks.py ........                                                                                                                                                                                                                                                                          [100%]
Saved benchmark data in: /Users/andrew/Documents/code/pydantic-aioredis/examples/benchmarks/.benchmarks/Darwin-CPython-3.10-64bit/0002_a8ba8e5626baf18a710577db946d52a6ddaed6fa_20220918_011903_uncommited-changes.json



------------------------------------------------------------------------------------------------------------------------------------ benchmark: 16 tests ------------------------------------------------------------------------------------------------------------------------------------
Name (time in us)                                                                                                   Min                   Max                Mean              StdDev              Median                 IQR            Outliers  OPS (Kops/s)            Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_bulk_insert[redis_store-aio_benchmark-models4-ModelWithPrefix-prefix:modelwithprefix:] (0001_a8ba8e5)     236.1250 (1.0)        575.1670 (1.18)     285.3251 (1.0)       35.3125 (1.80)     272.5420 (1.0)       25.5731 (1.47)        98;70        3.5048 (1.0)         645           1
test_bulk_insert[redis_store-aio_benchmark-models5-ModelWithSeparator-modelwithseparator!!] (NOW)              239.2500 (1.01)       524.4169 (1.07)     306.2764 (1.07)      63.9848 (3.27)     274.1665 (1.01)     102.2499 (5.86)         97;1        3.2650 (0.93)        442           1
test_bulk_insert[redis_store-aio_benchmark-models3-ModelWithIP-modelwithip:] (NOW)                             247.7920 (1.05)       544.1250 (1.12)     299.9481 (1.05)      35.7845 (1.83)     288.3755 (1.06)      27.1461 (1.56)        73;33        3.3339 (0.95)        436           1
test_bulk_insert[redis_store-aio_benchmark-models7-ModelWithFullCustomKey-prefix!!custom!!] (NOW)              252.1670 (1.07)       968.1670 (1.98)     345.5339 (1.21)      88.7134 (4.53)     335.8750 (1.23)     114.0832 (6.54)         25;9        2.8941 (0.83)        273           1
test_bulk_insert[redis_store-aio_benchmark-models6-ModelWithTableName-tablename:] (NOW)                        257.3340 (1.09)     1,078.4591 (2.21)     383.8750 (1.35)     132.0333 (6.74)     355.8125 (1.31)      99.1239 (5.68)        23;23        2.6050 (0.74)        238           1
test_bulk_insert[redis_store-aio_benchmark-models6-ModelWithTableName-tablename:] (0001_a8ba8e5)               257.6250 (1.09)     1,053.8750 (2.16)     346.8971 (1.22)     103.2863 (5.27)     328.8955 (1.21)     105.7080 (6.06)         11;8        2.8827 (0.82)        290           1
test_bulk_insert[redis_store-aio_benchmark-models4-ModelWithPrefix-prefix:modelwithprefix:] (NOW)              258.6249 (1.10)       835.5831 (1.71)     345.5334 (1.21)      85.7124 (4.37)     316.0409 (1.16)     117.2609 (6.72)         32;6        2.8941 (0.83)        271           1
test_bulk_insert[redis_store-aio_benchmark-models5-ModelWithSeparator-modelwithseparator!!] (0001_a8ba8e5)     261.9170 (1.11)       979.4589 (2.01)     368.7724 (1.29)     111.1759 (5.67)     346.8749 (1.27)     102.1872 (5.86)        20;13        2.7117 (0.77)        251           1
test_bulk_insert[redis_store-aio_benchmark-models2-ModelWithNone-modelwithnone:] (NOW)                         267.7920 (1.13)     1,136.8330 (2.33)     364.0978 (1.28)      99.5982 (5.08)     346.2080 (1.27)     127.4063 (7.31)         13;7        2.7465 (0.78)        257           1
test_bulk_insert[redis_store-aio_benchmark-models7-ModelWithFullCustomKey-prefix!!custom!!] (0001_a8ba8e5)     267.9999 (1.13)       779.0411 (1.60)     376.6928 (1.32)      87.3057 (4.46)     369.0000 (1.35)      85.1772 (4.88)        47;12        2.6547 (0.76)        207           1
test_bulk_insert[redis_store-aio_benchmark-models3-ModelWithIP-modelwithip:] (0001_a8ba8e5)                    286.6250 (1.21)     1,870.9170 (3.83)     425.0030 (1.49)     158.7233 (8.10)     398.2920 (1.46)     100.8335 (5.78)        21;21        2.3529 (0.67)        192           1
test_bulk_insert[redis_store-aio_benchmark-models2-ModelWithNone-modelwithnone:] (0001_a8ba8e5)                290.4161 (1.23)     1,206.3751 (2.47)     415.8359 (1.46)     129.6744 (6.62)     394.7085 (1.45)      88.8335 (5.09)        14;14        2.4048 (0.69)        180           1
test_bulk_insert[redis_store-aio_benchmark-models0-Book-book:] (NOW)                                           373.8340 (1.58)       487.9159 (1.0)      400.8765 (1.40)      20.5551 (1.05)     394.2915 (1.45)      17.4375 (1.0)         55;29        2.4945 (0.71)        276           1
test_bulk_insert[redis_store-aio_benchmark-models0-Book-book:] (0001_a8ba8e5)                                  374.8330 (1.59)       538.2920 (1.10)     399.7707 (1.40)      19.5931 (1.0)      393.6250 (1.44)      19.3750 (1.11)        58;15        2.5014 (0.71)        307           1
test_bulk_insert[redis_store-aio_benchmark-models1-ExtendedBook-extendedbook:] (0001_a8ba8e5)                  405.1670 (1.72)       782.5830 (1.60)     456.8254 (1.60)      71.1623 (3.63)     428.8960 (1.57)      33.9170 (1.95)        49;55        2.1890 (0.62)        384           1
test_bulk_insert[redis_store-aio_benchmark-models1-ExtendedBook-extendedbook:] (NOW)                           405.4171 (1.72)       754.2920 (1.55)     452.1815 (1.58)      53.4064 (2.73)     432.6666 (1.59)      24.4590 (1.40)        44;58        2.2115 (0.63)        396           1
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
============================================================================================================================================ 8 passed in 3.87s =============================================================================================================================================
```

Benchmarks will automatically compare the benchmark now vs your first run

## How this works

The benchmarks make use of <https://pytest-benchmark.readthedocs.io/en/latest/index.html>

## Benchmark status

The benchmarks are a work in progress. At this time, they're testing very basic inserts. More work could be done to add additional benchmarks
