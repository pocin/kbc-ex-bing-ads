from exbingads.utils import parse_config, write_manifest, clean_report
import os

def test_parsing_config():
    params, oauth = parse_config('/src/tests/data')
    assert len(params) == 4
    assert isinstance(params, dict)
    assert params['bucket'] == 'out.c-main'
    assert oauth == ["foo"]


def test_writing_manifest(tmpdir):
    pth = tmpdir.mkdir('test').join('report.csv')
    args = dict(
        csvpath=pth,
        bucket='in.c-ex-bingads-ex11',
        table='',
        incremental=True,
        pk_columns=['Id', 'Device']
    )
    path_manifest = write_manifest(**args)
    assert path_manifest == args['csvpath'] + '.manifest'
    assert os.path.isfile(path_manifest)


def test_cleaning_report(tmpdir):
    outdir = tmpdir.mkdir('outtables')
    report = tmpdir.mkdir('test').join('report.csv')
    row1 = 'ActualReport,Column2,Column3'
    row2 = 'Value1,Value2,Value3'
    report.write('''"Report Name: Ad_Performance"
"Report Time: 10/5/2017,10/11/2017"
"Time Zone: (GMT+08:00) Kuala Lumpur, Singapore"
"Last Completed Available Day: 10/3/2017 3:20:00 AM (GMT)"
"Last Completed Available Hour: 10/3/2017 3:20:00 AM (GMT)"
"Report Aggregation: Daily"
"Report Filter: "
"Potential Incomplete Data: true"
"Rows: 24"

{row1}
{row2}
    '''.format(row1=row1, row2=row2))
    outpath = clean_report(report, outdir, suffix='_clean')
    assert outpath == os.path.join(outdir.strpath, 'report_clean.csv')
    with open(outpath) as f:
        assert next(f).strip() == row1
        assert next(f).strip() == row2



