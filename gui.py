import json
import time
from pathlib import Path

from logging import NOTSET, LogRecord, Handler, Formatter
# from datetime import datetime

from fastapi import Request
from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from common.logger import logger, Log
from main import Leader


base_url = r'http://127.0.0.1:8050'


@app.route('/baseUrl')
async def get_base_url(request: Request):
    base = request.base_url
    return {'baseUrl': base}


app.add_static_files(
    '/runtime_logs',
    local_directory='runtime_logs',
    follow_symlink=False
)


# add Quasar style
ui.add_sass('''
.sticky-header-column-table
  /* height or max-height is important */
  height: 310px

  /* specifying max-width so the example can
    highlight the sticky column on any browser window */
  max-width: 600px

  td:first-child
    /* bg color is important for td; just specify one */
    background-color:  #ebedef

  tr th
    position: sticky
    /* higher than z-index for td below */
    z-index: 2
    /* bg color is important; just specify one */
    background:  #ebedef

  /* this will be the loading indicator */
  thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
    /* highest z-index */
    z-index: 3
  thead tr:first-child th
    top: 0
    z-index: 1
  tr:first-child th:first-child
    /* highest z-index */
    z-index: 3

  td:first-child
    z-index: 1

  td:first-child, th:first-child
    position: sticky
    left: 0

  /* prevent scrolling behind sticky top row on focus */
  tbody
    /* height of all previous header rows */
    scroll-margin-top: 48px
''')


class LogElementHandler(Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log, level: int = NOTSET) -> None:
        self.element = element
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        try:
            msg = self.format(record)
            self.element.push(msg)
        except Exception:
            self.handleError(record)


class MainWindow:

    def __init__(self) -> None:
        Log.configure()
        self.log_view = None
        self.leader = Leader()
        self.error_bits = None

    def main(self):
        # add a local directory available at the  service specified endpoint,
        # base = requests.get('/baseUrl', timeout=2)
        with ui.card().classes('w-full h-1/2 no-shadow border-[2px] border-dashed'):
            with ui.row(wrap=False, align_items='start').classes('w-full h-full'):
                with ui.column().classes('w-1/2 h-full outline p-1 outline-blue-500'):
                    with ui.row().classes() as row:
                        row.tailwind.align_items('center')
                        ui.label('DUT master address:')
                        ui.input(
                            placeholder='DUT master ip address',
                            on_change=lambda e: logger.info(f'DUT master ip address: {e.value}'),
                            validation={'Input too long': lambda value: len(value) < 16 if value else True}
                        ).props('clearable')
                    with ui.row().classes() as row:
                        row.tailwind.align_items('center')
                        ui.label('DUT master username:')
                        ui.input(
                            placeholder='DUT master username',
                            on_change=lambda e: logger.info(f'DUT master username: {e.value}'),
                            validation={'Input too long': lambda value: len(value) < 50 if value else True}
                        ).props('clearable')
                    with ui.row() as row:
                        row.tailwind.align_items('center')
                        ui.label('DUT master password:')
                        ui.input(
                            placeholder='DUT master password',
                            on_change=lambda e: logger.info(f'DUT master password: {e.value}'),
                            validation={'Input too long': lambda value: len(value) < 100 if value else True},
                            password=True,
                            password_toggle_button=True
                        ).props('clearable')
                    with ui.row() as row:
                        row.tailwind.align_items('center')
                        ui.label('DUT errorBits:')
                        ui.input(
                            placeholder='DUT errorBits input example: 0x5, 0x20000',
                            on_change=self.on_update_error_bits,
                            validation={'Input too long': lambda value: len(value) < 100 if value else True},
                            password=False
                        ).props('clearable')
                    ui.separator().classes('outline-dashed outline-1')
                    # with ui.card_section().classes('w-full'):
                    self.log_view = ui.log(max_lines=20).classes('w-full h-200 outline-blue-500 outline-2')
                    # log_view.clear()
                    # ui.button('Run', on_click=lambda x: self.log_view.push(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                    ui.button('Run', on_click=self.capture)

                with ui.column().classes('w-1/2 h-full outline p-1 outline-blue-500'):
                    table_headers = [
                        {
                            'name': 'datetime',
                            'label': 'Datetime',
                            'field': 'datetime',
                            'required': True,
                            'align': 'left'
                        },
                        {
                            'name': 'errorBits',
                            'label': 'ErrorBits',
                            'field': 'errorBits',
                            'required': True,
                            'align': 'left',
                            'sortable': True
                        },
                        {
                            'name': 'BTSLog',
                            'label': 'BTSLog',
                            'field': 'BTSLog',
                            'required': True,
                            'align': 'center'
                        },
                        {
                            'name': 'runtimeLog',
                            'label': 'RuntimeLog',
                            'field': 'runtimeLog',
                            'required': True,
                            'align': 'center'
                        },
                    ]
                    table_rows = [
                        {'datetime': '2014-08-21 00:00:00', 'errorBits': '0x5', 'runtimeLog': '.log'},
                        {'datetime': '2014-08-21 00:00:10', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:20', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:30', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:40', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:50', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:60', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:70', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:00', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:10', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:20', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:30', 'errorBits': '0x20', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:40', 'errorBits': '0x5', 'runtimeLog': 'null'},
                        {'datetime': '2014-08-21 00:00:50', 'errorBits': '0x20', 'runtimeLog': 'null'},
                    ]
                    with ui.table(
                        columns=table_headers,
                        rows=None,
                        row_key='datetime',
                        title='runtimeLog Table',
                        selection='single',
                        pagination=10
                    ).style('height: 612px;').classes(
                        'sticky-header-column-table w-full h-full'
                    ).props('virtual-scroll') as table:
                        table.add_rows()
                        # with table.add_slot('bottom-row'):
                        #     ui.button(
                        #         'download',
                        #         on_click=lambda: ui.download(
                        #             '/runtime_logs/SYSLOG_040983.LOG',
                        #             filename='SYSLOG_040983.LOG'
                        #         )
                        #     )
                            
                        def download():
                            ...

                        table.add_slot(
                            "body-cell-runtimeLog",
                            """
                            <q-td key="BTSLog" :props="props" auto-width>
                                <q-btn icon-right="download" :label="props.value" no-caps flat fab-mini 
                                    color="primary" @click="$parent.$emit('download', props.row)" />
                            </q-td>
                            <q-td key="runtimeLog" :props="props" auto-width>
                                <q-btn icon-right="download" :label="props.value" no-caps flat fab-mini 
                                    color="primary" @click="$parent.$emit('download', props.row)" />
                            </q-td>
                            """
                        )
                        table.on('download', download)
                        with table.row():
                            ...

    # def on_change_input(self, event: ValueChangeEventArguments):
    #     # print(event.value, type(event), event.sender)
    #     logger.info(f'DUT master ip address: {event.value}')

    def attach_to_logger(self):
        if self.log_view is None:
            return
        handler = LogElementHandler(self.log_view)
        fmt = '%(asctime)s-%(filename)s:%(funcName)s:%(lineno)s => %(message)s'
        formatter = Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        ui.context.client.on_disconnect(lambda: logger.removeHandler(handler))

    def run(self, host: str, port: int, title: str = 'DDTT monitor'):
        ui.run(
            host=host,
            port=port,
            title=title,
            # eva-icons:'https://akveo.github.io/eva-icons/outline/png/128/video-outline.png'
            favicon='https://akveo.github.io/eva-icons/outline/png/128/video-outline.png'
        )
    
    def capture(self, log_dir: str, demo: bool = False):
        self.leader.poll_system_log_files(
            log_dir,
            error_bits=self.error_bits,
            demo=demo
        )

    def on_update_error_bits(self, event: ValueChangeEventArguments):
        self.error_bits = event.value.split(',')
        logger.info(f'errorBits: {self.error_bits}')
        setting_path = Path('./config/setting.json')
        with open(setting_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            logger.info(f' reading settings: {settings}')
            dut_params = settings.get('dut_params')
            dut_params.update({'error_bits': self.error_bits})
            logger.info(f'settings updated: {settings}')
        with open(setting_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
            time.sleep(0.5)


if __name__ in {"__main__", "__mp_main__"}:
    main_window = MainWindow()
    main_window.main()
    main_window.attach_to_logger()
    main_window.run('127.0.0.1', 8050)
