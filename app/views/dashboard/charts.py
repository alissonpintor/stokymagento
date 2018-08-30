import pygal as pl
from pygal.style import CleanStyle, LightenStyle
from pygal.style import TurquoiseStyle
from pygal.style import Style
import locale
import calendar


locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')


def getHalfPie(title, data):
    config = pl.Config()
    config.title = title
    config.show_legend = False
    config.human_readable = True
    # config.value_formatter = lambda x: locale.currency(x, grouping=True)
    config.half_pie = True
    config.inner_radius = 0.70
    # config.spacing = 120
    config.style = getChartStyle()

    gauge = pl.SolidGauge(config, value_formatter = lambda x: locale.currency(x, grouping=True))

    for key, obj in data.items():
        gauge.add(key, [{'value': obj.get('value'), 
                         'max_value': obj.get('max_value'), 
                         'label': 'Meta:{}'.format(obj.get('label'))
                        }])

    return gauge.render_data_uri()

def getHorizontalBar(title, data, isMobile=False):
    barType = pl.HorizontalBar if isMobile else pl.Bar
    
    config = pl.Config()
    config.legend_at_bottom = True
    config.value_formatter = lambda x: locale.currency(x, grouping=True)
    config.legend_box_size = 26
    config.style = getChartStyle()

    if isMobile:
        config.height = 1000

    barChart = barType(config)
    barChart.title = title
    if isinstance(data, dict):
        for key, value in data.items():
            nome = key.split()
            nome = '{} {}'.format(nome[0], nome[-1])
            barChart.add(nome, value)
    
    return barChart.render_data_uri()


def getChartVendasAnoMes(valueList, isMobile=None):
    config = pl.Config()
    config.legend_at_bottom = True
    config.fill = True
    config.dots_size = 5
    config.legend_at_bottom_columns = 3
    config.value_formatter = lambda x: locale.currency(x, grouping=True)

    style = CleanStyle(base_style=TurquoiseStyle)
    if isMobile:
        config.dots_size = 10
        # style.value_font_size = 35
        style.title_font_size = 35 
        style.tooltip_font_size = 25 
        style.font_family = 'googlefont:Barlow'

    lineChart = pl.Line(config, style=style)
    lineChart.title = ('Comparativo de Vendas Anual')
    lineChart.x_labels = [mes.upper()[0:3] for mes in calendar.month_name[1:]]

    for value in valueList:
        lineChart.add(*value)
    
    return lineChart.render_data_uri()


def getChartStyle(screenWidth=1900):
    custom_style = Style(
        value_colors='blue',
        plot_background='#FBFBFC',
        font_family='googlefont:Barlow'
    )

    if(screenWidth <= 700 ):
        custom_style.value_font_size = 35
        custom_style.title_font_size = 35
        custom_style.tooltip_font_size = 35
    elif(screenWidth <= 990):
        custom_style.value_font_size = 35
        custom_style.title_font_size = 35
        custom_style.tooltip_font_size = 35
    elif(screenWidth <= 1400):
        custom_style.value_font_size = 35
        custom_style.title_font_size = 35
        custom_style.tooltip_font_size = 35
    else:
        custom_style.value_font_size = 35
        custom_style.title_font_size = 35
        custom_style.tooltip_font_size = 35
    
    return custom_style
