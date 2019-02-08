from abc import abstractmethod, ABCMeta
from os.path import join
from typing import List

from qf_lib.analysis.timeseries_analysis.timeseries_analysis import TimeseriesAnalysis
from qf_lib.common.enums.plotting_mode import PlottingMode
from qf_lib.common.utils.document_exporting import Document, GridElement
from qf_lib.common.utils.document_exporting.element.page_header import PageHeaderElement
from qf_lib.common.utils.document_exporting.element.table import Table
from qf_lib.common.utils.document_exporting.pdf_exporter import PDFExporter
from qf_lib.containers.series.qf_series import QFSeries
from qf_lib.plotting.charts.line_chart import LineChart
from qf_lib.plotting.charts.underwater_chart import UnderwaterChart
from qf_lib.plotting.decorators.axes_label_decorator import AxesLabelDecorator
from qf_lib.plotting.decorators.data_element_decorator import DataElementDecorator
from qf_lib.plotting.decorators.legend_decorator import LegendDecorator
from qf_lib.plotting.decorators.line_decorators import HorizontalLineDecorator
from qf_lib.plotting.decorators.title_decorator import TitleDecorator
from qf_lib.plotting.decorators.top_drawdown_decorator import TopDrawdownDecorator
from qf_lib.settings import Settings
from qf_lib.starting_dir import get_starting_dir_abs_path


class AbstractDocument(metaclass=ABCMeta):
    """
    Base class for Most PDF document with charts and tables.
    """

    def __init__(self, settings: Settings, pdf_exporter: PDFExporter, title: str = "Document Title"):
        self.title = title
        self.document = Document(title)
        self.full_image_size = (8, 2.4)

        # position is linked to the position of axis in tearsheet.mplstyle
        self.full_image_axis_position = (0.08, 0.1, 0.892, 0.80)
        self.half_image_size = (4, 2.2)
        self.dpi = 400

        self.settings = settings
        self.pdf_exporter = pdf_exporter

    @abstractmethod
    def build_document(self):
        # main function that composes the document
        pass

    @abstractmethod
    def save(self, report_dir: str = ""):
        # function that saves the document on the disk
        pass

    def _get_new_grid(self) -> GridElement:
        return GridElement(mode=PlottingMode.PDF, figsize=self.half_image_size, dpi=self.dpi)

    def _add_header(self):
        logo_path = join(get_starting_dir_abs_path(), self.settings.logo_path)
        company_name = self.settings.company_name

        self.document.add_element(PageHeaderElement(logo_path, company_name, self.title))

    def _get_underwater_chart(self, series: QFSeries):
        underwater_chart = UnderwaterChart(series, rotate_x_axis=True)
        underwater_chart.add_decorator(TopDrawdownDecorator(series, 5))
        underwater_chart.add_decorator(AxesLabelDecorator(y_label="Drawdown"))
        underwater_chart.add_decorator(TitleDecorator("Drawdown"))
        return underwater_chart

    def _get_perf_chart(self, series_list):
        strategy = series_list[0].to_prices(1)
        log_scale = True if strategy[-1] > 5 else False  # use log scale for returns above 500 %
        chart = LineChart(start_x=strategy.index[0], end_x=strategy.index[-1], log_scale=log_scale)
        line_decorator = HorizontalLineDecorator(1, key="h_line", linewidth=1)
        chart.add_decorator(line_decorator)
        legend = LegendDecorator()
        for series in series_list:
            strategy_tms = series.to_prices(1)
            series_elem = DataElementDecorator(strategy_tms)
            chart.add_decorator(series_elem)

            legend.add_entry(series_elem, strategy_tms.name)
        chart.add_decorator(legend)
        title_decorator = TitleDecorator("Strategy Performance", key="title")
        chart.add_decorator(title_decorator)
        return chart

    def _get_leverage_chart(self, leverage: QFSeries):
        chart = LineChart()

        series_elem = DataElementDecorator(leverage)
        chart.add_decorator(series_elem)

        title_decorator = TitleDecorator("Leverage over time", key="title")
        chart.add_decorator(title_decorator)
        return chart

    def _add_statistics_table(self, ta_list: List[TimeseriesAnalysis]):
        table = Table(css_class="table stats-table")

        for ta in ta_list:
            ta.populate_table(table)
        self.document.add_element(table)