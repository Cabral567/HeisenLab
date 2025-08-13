from__future__importannotations

importos
fromtypingimportOptional
importwarnings

importpandasaspd
importnumpyasnp
fromPySide6.QtCoreimportQt
fromPySide6.QtWidgetsimport(
QWidget,
QVBoxLayout,
QHBoxLayout,
QGridLayout,
QPushButton,
QLabel,
QFileDialog,
QComboBox,
QMessageBox,
QGroupBox,
QCheckBox,
QTabWidget,
QTextEdit,
QSpinBox,
QDoubleSpinBox,
QInputDialog,
QProgressBar,
QListWidget,
)

from..plottingimportMplCanvas,FullScreenPlotDialog
frommatplotlib.backends.backend_qtaggimportNavigationToolbar2QT
importmatplotlib.pyplotasplt

#Bibliotecascientíficasespecializadas
try:
fromscipyimportsignal
fromsklearn.preprocessingimportStandardScaler,MinMaxScaler
fromsklearn.decompositionimportPCA
fromlmfitimportmodels
HAS_SCIPY=True
HAS_SKLEARN=True
HAS_LMFIT=True
exceptImportError:
HAS_SCIPY=False
HAS_SKLEARN=False
HAS_LMFIT=False

try:
importpeakutils
HAS_PEAKUTILS=True
exceptImportError:
HAS_PEAKUTILS=False

warnings.filterwarnings('ignore')


classVoltammogramTab(QWidget):
def__init__(self,parent=None):
super().__init__(parent)

self.df:Optional[pd.DataFrame]=None
self.sample_names=None
self.canvas=MplCanvas()

#Adicionabarradeferramentasdomatplotlib
self.toolbar=NavigationToolbar2QT(self.canvas,self)

#Configurainterfaceprincipal
self.setup_ui()

defsetup_ui(self):
"""Configuraainterfacecommúltiplasabasdeanálise"""
layout=QVBoxLayout(self)

#Seçãodecarregamentodearquivo
file_group=QGroupBox("ArquivodeDados")
file_layout=QVBoxLayout(file_group)

self.load_btn=QPushButton("CarregararquivoExcel(.xlsx)")
self.load_btn.clicked.connect(self._load_file)

self.file_label=QLabel("Nenhumarquivocarregado")
self.file_label.setStyleSheet("color:#666;font-style:italic;")

file_layout.addWidget(self.load_btn)
file_layout.addWidget(self.file_label)

#Abasdeanálise
self.tabs=QTabWidget()

#Aba1:AnáliseBásica(códigoatual)
self.basic_tab=self._create_basic_analysis_tab()
self.tabs.addTab(self.basic_tab,"AnáliseBásica")

#Aba2:VoltametriaAvançada
ifHAS_SCIPYorHAS_LMFIT:
self.advanced_tab=self._create_advanced_voltammetry_tab()
self.tabs.addTab(self.advanced_tab,"VoltametriaAvançada")

#Aba3:ProcessamentodeSinal
ifHAS_SCIPY:
self.signal_tab=self._create_signal_processing_tab()
self.tabs.addTab(self.signal_tab,"ProcessamentodeSinal")

#Aba4:AnáliseEstatística
ifHAS_SKLEARN:
self.stats_tab=self._create_statistical_analysis_tab()
self.tabs.addTab(self.stats_tab,"AnáliseEstatística")

#Layoutprincipal
layout.addWidget(file_group)
layout.addWidget(self.tabs)

#Controlesdevisualizaçãodográfico
viz_group=QGroupBox("ControlesdeVisualização")
viz_layout=QHBoxLayout(viz_group)

self.fullscreen_btn=QPushButton("TelaCheia")
self.fullscreen_btn.clicked.connect(self._show_fullscreen_plot)
self.fullscreen_btn.setToolTip("Abrirgráficoemjanelaseparada(F11)")

self.refresh_btn=QPushButton("Atualizar")
self.refresh_btn.clicked.connect(self._refresh_plot)
self.refresh_btn.setToolTip("Atualizarvisualizaçãodográfico")

self.zoom_fit_btn=QPushButton("AjustarZoom")
self.zoom_fit_btn.clicked.connect(self._zoom_fit)
self.zoom_fit_btn.setToolTip("Ajustarzoomparamostrartodososdados")

viz_layout.addWidget(self.fullscreen_btn)
viz_layout.addWidget(self.refresh_btn)
viz_layout.addWidget(self.zoom_fit_btn)
viz_layout.addStretch()

layout.addWidget(viz_group)
layout.addWidget(self.toolbar)
layout.addWidget(self.canvas)

#Infolabel
self.info_label=QLabel("")
self.info_label.setStyleSheet("color:#333;margin:5px;")
layout.addWidget(self.info_label)

def_create_basic_analysis_tab(self):
"""Criaabadeanálisebásica(funcionalidadeatual)"""
tab=QWidget()
layout=QVBoxLayout(tab)

#DetecçãodeparesPotencial-Corrente
detection_group=QGroupBox("ConfiguraçõesdePlotagem")
detection_layout=QVBoxLayout(detection_group)

self.auto_detect_btn=QPushButton("DetectarParesPotencial-Corrente")
self.auto_detect_btn.clicked.connect(self._auto_detect_pairs)
detection_layout.addWidget(self.auto_detect_btn)

self.pairs_list=QListWidget()
detection_layout.addWidget(QLabel("Paresdetectados:"))
detection_layout.addWidget(self.pairs_list)

#Configuraçõesdeajustepolinomial
fit_group=QGroupBox("AjustePolinomial")
fit_layout=QGridLayout(fit_group)

fit_layout.addWidget(QLabel("Graudopolinômio:"),0,0)
self.degree_spin=QSpinBox()
self.degree_spin.setRange(2,5)
self.degree_spin.setValue(4)
fit_layout.addWidget(self.degree_spin,0,1)

self.plot_btn=QPushButton("PlotarVoltamogramas")
self.plot_btn.clicked.connect(self._plot_voltammograms)
self.plot_btn.setEnabled(False)
fit_layout.addWidget(self.plot_btn,1,0,1,2)

#Botãodeteste(temporário)
self.test_btn=QPushButton("TesteGráfico")
self.test_btn.clicked.connect(self._test_plot)
fit_layout.addWidget(self.test_btn,2,0,1,2)

layout.addWidget(detection_group)
layout.addWidget(fit_group)
layout.addStretch()

returntab

def_create_advanced_voltammetry_tab(self):
"""Criaabadevoltametriaavançadacomanálisesespecíficas"""
tab=QWidget()
layout=QVBoxLayout(tab)

#AnálisedePicos
peak_group=QGroupBox("AnálisedePicos")
peak_layout=QGridLayout(peak_group)

peak_layout.addWidget(QLabel("Alturamínima:"),0,0)
self.peak_height_spin=QDoubleSpinBox()
self.peak_height_spin.setRange(0.001,1000.0)
self.peak_height_spin.setValue(0.1)
self.peak_height_spin.setSuffix("µA")
peak_layout.addWidget(self.peak_height_spin,0,1)

peak_layout.addWidget(QLabel("Distânciamínima:"),1,0)
self.peak_distance_spin=QSpinBox()
self.peak_distance_spin.setRange(1,100)
self.peak_distance_spin.setValue(10)
self.peak_distance_spin.setSuffix("pontos")
peak_layout.addWidget(self.peak_distance_spin,1,1)

self.find_peaks_btn=QPushButton("EncontrarPicos")
self.find_peaks_btn.clicked.connect(self._find_peaks)
peak_layout.addWidget(self.find_peaks_btn,2,0,1,2)

#AnáliseCinética
kinetic_group=QGroupBox("AnáliseCinética")
kinetic_layout=QGridLayout(kinetic_group)

kinetic_layout.addWidget(QLabel("Velocidadedevarredura(V/s):"),0,0)
self.scan_rate_spin=QDoubleSpinBox()
self.scan_rate_spin.setRange(0.001,10.0)
self.scan_rate_spin.setValue(0.1)
kinetic_layout.addWidget(self.scan_rate_spin,0,1)

self.kinetic_analysis_btn=QPushButton("AnáliseRandles-Sevcik")
self.kinetic_analysis_btn.clicked.connect(self._kinetic_analysis)
kinetic_layout.addWidget(self.kinetic_analysis_btn,1,0,1,2)

layout.addWidget(peak_group)
layout.addWidget(kinetic_group)
layout.addStretch()

returntab

def_create_signal_processing_tab(self):
"""Criaabadeprocessamentodesinal"""
tab=QWidget()
layout=QVBoxLayout(tab)

#Filtros
filter_group=QGroupBox("Filtros")
filter_layout=QGridLayout(filter_group)

filter_layout.addWidget(QLabel("Tipodefiltro:"),0,0)
self.filter_combo=QComboBox()
self.filter_combo.addItems([
"Savitzky-Golay",
"Mediana",
"Gaussiano"
])
filter_layout.addWidget(self.filter_combo,0,1)

filter_layout.addWidget(QLabel("Parâmetro:"),1,0)
self.filter_param_spin=QSpinBox()
self.filter_param_spin.setRange(3,51)
self.filter_param_spin.setValue(11)
filter_layout.addWidget(self.filter_param_spin,1,1)

self.apply_filter_btn=QPushButton("AplicarFiltro")
self.apply_filter_btn.clicked.connect(self._apply_filter)
filter_layout.addWidget(self.apply_filter_btn,2,0,1,2)

layout.addWidget(filter_group)
layout.addStretch()

returntab

def_create_statistical_analysis_tab(self):
"""Criaabadeanáliseestatística"""
tab=QWidget()
layout=QVBoxLayout(tab)

#PCA
pca_group=QGroupBox("AnálisedeComponentesPrincipais(PCA)")
pca_layout=QGridLayout(pca_group)

pca_layout.addWidget(QLabel("Componentes:"),0,0)
self.pca_components_spin=QSpinBox()
self.pca_components_spin.setRange(2,10)
self.pca_components_spin.setValue(2)
pca_layout.addWidget(self.pca_components_spin,0,1)

self.pca_btn=QPushButton("ExecutarPCA")
self.pca_btn.clicked.connect(self._perform_pca)
pca_layout.addWidget(self.pca_btn,1,0,1,2)

#EstatísticasDescritivas
stats_group=QGroupBox("EstatísticasDescritivas")
stats_layout=QVBoxLayout(stats_group)

self.stats_btn=QPushButton("📋GerarRelatórioEstatístico")
self.stats_btn.clicked.connect(self._generate_stats_report)
stats_layout.addWidget(self.stats_btn)

self.stats_text=QTextEdit()
self.stats_text.setMaximumHeight(200)
stats_layout.addWidget(self.stats_text)

#Exportação
export_group=QGroupBox("Exportação")
export_layout=QGridLayout(export_group)

self.export_excel_btn=QPushButton("ExportarExcel")
self.export_excel_btn.clicked.connect(self._export_excel)
export_layout.addWidget(self.export_excel_btn,0,0)

self.export_csv_btn=QPushButton("ExportarCSV")
self.export_csv_btn.clicked.connect(self._export_csv)
export_layout.addWidget(self.export_csv_btn,0,1)

self.export_plot_btn=QPushButton("ExportarGráfico")
self.export_plot_btn.clicked.connect(self._export_plot)
export_layout.addWidget(self.export_plot_btn,1,0,1,2)

layout.addWidget(pca_group)
layout.addWidget(stats_group)
layout.addWidget(export_group)
layout.addStretch()

returntab

#===MÉTODOSDAABAANÁLISEBÁSICA===

def_load_file(self):
"""CarregaarquivoExcelcomdadosdevoltametria"""
file_path,_=QFileDialog.getOpenFileName(
self,"CarregararquivoExcel","",
"Excelfiles(*.xlsx*.xls);;Allfiles(*.*)"
)

iffile_path:
try:
#CarregarExcel
self.df=pd.read_excel(file_path,header=0)

#Extrairnomesdasamostrassehouverpadrão
self.sample_names=self._extract_sample_names(self.df.columns)

self.file_label.setText(f"Arquivocarregado:{file_path.split('/')[-1]}")
self.file_label.setStyleSheet("color:#2e7d32;font-weight:bold;")
self.info_label.setText(f"📊{len(self.df.columns)}colunas,{len(self.df)}linhas")

#Resetarcomponentesrelacionadosadados
ifhasattr(self,'pairs_list'):
self.pairs_list.clear()
ifhasattr(self,'plot_btn'):
self.plot_btn.setEnabled(False)

exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erroaocarregararquivo:\n{str(e)}")
self.file_label.setText("❌Erronocarregamento")
self.file_label.setStyleSheet("color:#d32f2f;")

def_extract_sample_names(self,columns):
"""Extrainomesdasamostrasdoscabeçalhosdascolunas"""
#Procurarpadrõescomo"Sample1_Potential","Amostra1_Corrente",etc.
sample_names=set()
forcolincolumns:
#Padrõescomuns
if'_'incol:
parts=col.split('_')
iflen(parts)>=2:
potential_sample=parts[0]
sample_names.add(potential_sample)

ifsample_names:
returnsorted(list(sample_names))
returnNone

def_auto_detect_pairs(self):
"""DetectaautomaticamenteparesdecolunasPotencial-Corrente"""
ifself.dfisNone:
#Senãoháarquivo,criardadosdeteste
reply=QMessageBox.question(self,"Semdados",
"Nenhumarquivocarregado.Desejacriardadosdeteste?",
QMessageBox.Yes|QMessageBox.No)
ifreply==QMessageBox.Yes:
self._create_test_data()
return
else:
QMessageBox.warning(self,"Erro","Primeirocarregueumarquivo!")
return

pairs=self._detect_voltage_pairs_from_structure(self.df)

self.pairs_list.clear()
fori,(potential_col,current_col)inenumerate(pairs):
#Usasample_namessedisponível,senãousanumeraçãosimples
ifself.sample_namesandi<len(self.sample_names):
sample_name=self.sample_names[i]
else:
sample_name=f"Amostra{i+1}"

item_text=f"{sample_name}:{potential_col}vs{current_col}"
self.pairs_list.addItem(item_text)

self.voltage_pairs=pairs
self.plot_btn.setEnabled(True)
self.info_label.setText(f"✅{len(pairs)}paresdetectados")

#Senãoencontroupares,darsugestões
iflen(pairs)==0:
msg="❌NenhumparPotencial-Correntedetectado!\n\n"
msg+="Colunasdisponíveis:\n"
fori,colinenumerate(self.df.columns):
msg+=f"{i+1}.{col}\n"
msg+="\nVerifiqueseascolunastêmnomescomo:\n"
msg+="-Potencial,Voltage,V,E\n"
msg+="-Corrente,Current,I,A"

QMessageBox.information(self,"Info-DetecçãodePares",msg)

def_create_test_data(self):
"""Criadadosdetesteparademonstração"""
try:
#Criardadosdevoltametriasimulados
potential=np.linspace(-1.5,1.5,100)

#Amostra1:Picoem0.2V
current1=2.5*np.exp(-((potential-0.2)/0.3)**2)+np.random.normal(0,0.05,100)

#Amostra2:Picoem-0.3V
current2=3.2*np.exp(-((potential+0.3)/0.25)**2)+np.random.normal(0,0.07,100)

#Amostra3:Doispicos
current3=(1.8*np.exp(-((potential-0.5)/0.2)**2)+
2.1*np.exp(-((potential+0.7)/0.3)**2)+
np.random.normal(0,0.04,100))

#CriarDataFrame
self.df=pd.DataFrame({
'Potencial_1':potential,
'Corrente_1':current1,
'Potencial_2':potential,
'Corrente_2':current2,
'Potencial_3':potential,
'Corrente_3':current3
})

self.sample_names=['Teste_1','Teste_2','Teste_3']

self.file_label.setText("✅Dadosdetestecriados")
self.file_label.setStyleSheet("color:#2e7d32;font-weight:bold;")
self.info_label.setText("📊Dadosdetestecarregados:3amostrassimuladas")

#Auto-detectarosparescriados
pairs=self._detect_voltage_pairs_from_structure(self.df)

self.pairs_list.clear()
fori,(potential_col,current_col)inenumerate(pairs):
sample_name=self.sample_names[i]ifi<len(self.sample_names)elsef"Amostra{i+1}"
item_text=f"{sample_name}:{potential_col}vs{current_col}"
self.pairs_list.addItem(item_text)

self.voltage_pairs=pairs
self.plot_btn.setEnabled(True)
self.info_label.setText(f"✅{len(pairs)}paresdetestedetectados")

exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erroaocriardadosdeteste:{str(e)}")
print(f"Errodetalhado:{e}")
importtraceback
traceback.print_exc()

def_detect_voltage_pairs_from_structure(self,df):
"""DetectaparesPotencial-Correntebaseadonaestruturadascolunas"""
pairs=[]
columns=df.columns.tolist()

#Estratégia1:Buscarpadrõescompalavras-chave
potential_keywords=['potential','potencial','voltage','volt','v','e']
current_keywords=['current','corrente','ampere','amp','i','a']

potential_cols=[]
current_cols=[]

forcolincolumns:
col_lower=col.lower()

#Verificarseécolunadepotencial
ifany(keywordincol_lowerforkeywordinpotential_keywords):
potential_cols.append(col)
#Verificarseécolunadecorrente
elifany(keywordincol_lowerforkeywordincurrent_keywords):
current_cols.append(col)

#Estratégia2:Senãoencontroucompalavras-chave,usarposiçãoalternada
ifnotpotential_colsandnotcurrent_cols:
#Assumirquecolunasestãoalternadas:Potencial,Corrente,Potencial,Corrente...
foriinrange(0,len(columns)-1,2):
potential_cols.append(columns[i])
ifi+1<len(columns):
current_cols.append(columns[i+1])

#Parearascolunas
min_len=min(len(potential_cols),len(current_cols))
foriinrange(min_len):
pairs.append((potential_cols[i],current_cols[i]))

returnpairs

def_plot_voltammograms(self):
"""Plotavoltamogramascomajustepolinomial"""
ifnothasattr(self,'voltage_pairs'):
QMessageBox.warning(self,"Erro","Detecteosparesprimeiro!")
return

self._plot_voltage_pairs(self.voltage_pairs,degree=self.degree_spin.value())

def_plot_voltage_pairs(self,pairs,degree=4):
"""Plotaparesdevoltagemcomajustepolinomial"""
self.canvas.ax.clear()

colors=plt.cm.Set1(np.linspace(0,1,len(pairs)))

fori,(potential_col,current_col)inenumerate(pairs):
color=colors[i]

#Extrairdados
potential=self.df[potential_col].dropna().values
current=self.df[current_col].dropna().values

#Garantirquetenhamomesmotamanho
min_len=min(len(potential),len(current))
potential=potential[:min_len]
current=current[:min_len]

iflen(potential)==0:
continue

#Plotpontosexperimentais
label_exp=f'Amostra{i+1}'ifself.sample_namesisNoneelseself.sample_names[i]ifi<len(self.sample_names)elsef'Amostra{i+1}'

self.canvas.ax.plot(potential,current,'o',color=color,
alpha=0.7,markersize=4,label=f'Exp.{label_exp}')

#Ajustepolinomial
try:
coeffs=np.polyfit(potential,current,degree)
potential_fit=np.linspace(potential.min(),potential.max(),300)
current_fit=np.polyval(coeffs,potential_fit)

self.canvas.ax.plot(potential_fit,current_fit,'-',color=color,
linewidth=2,alpha=0.8,label=f'AjustePoli.{label_exp}')

exceptExceptionase:
print(f"Erronoajustepolinomialpara{potential_col}:{e}")

self._configure_plot()
self.info_label.setText(f"✅{len(pairs)}voltamogramasplotadoscomajustepolinomial(grau{degree})")

def_configure_plot(self):
"""Configuraaparênciadográfico"""
ax=self.canvas.ax

#Labelsetítulo
ax.set_xlabel('Potencial(V)',fontsize=12,fontweight='bold')
ax.set_ylabel('Corrente(µA)',fontsize=12,fontweight='bold')
ax.set_title('Voltamogramas',fontsize=14,fontweight='bold',pad=20)

#Grid
ax.grid(True,alpha=0.3,linestyle='-',linewidth=0.5)

#Estilodoseixos
ax.tick_params(axis='both',which='major',labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

#Configurarlegenda
self._configure_legend(ax,"Direita")

#Ajustarlayoutparaacomodarlegenda
plt.subplots_adjust(right=0.75)

self.canvas.draw()

def_configure_legend(self,ax,legend_pos):
"""Configuraalegendadográfico"""
ifnotax.get_legend_handles_labels()[0]:#Senãoháelementosparalegenda
return

iflegend_pos=="Direita":
legend=ax.legend(bbox_to_anchor=(1.02,1),loc='upperleft',
fontsize=10,frameon=True,fancybox=False,shadow=False,
edgecolor='black',facecolor='white')
else:#Automático
legend=ax.legend(loc='best',fontsize=10,frameon=True,
fancybox=False,shadow=False,edgecolor='black',facecolor='white')

#===MÉTODOSDASABASAVANÇADAS(apenasstubssebibliotecasnãodisponíveis)===

def_find_peaks(self):
"""Encontrapicosnosvoltamogramas"""
ifnotHAS_SCIPY:
QMessageBox.warning(self,"FuncionalidadeIndisponível",
"Instale'scipy'parausarestafuncionalidade:\npipinstallscipy")
return

QMessageBox.information(self,"Info","Funcionalidadededetecçãodepicosemdesenvolvimento")

def_kinetic_analysis(self):
"""AnálisecinéticaRandles-Sevcik"""
QMessageBox.information(self,"Info","Análisecinéticaemdesenvolvimento")

def_apply_filter(self):
"""Aplicafiltronosdados"""
ifnotHAS_SCIPY:
QMessageBox.warning(self,"FuncionalidadeIndisponível",
"Instale'scipy'parausarestafuncionalidade:\npipinstallscipy")
return

QMessageBox.information(self,"Info","Filtrosemdesenvolvimento")

def_perform_pca(self):
"""RealizaanálisePCA"""
ifnotHAS_SKLEARN:
QMessageBox.warning(self,"FuncionalidadeIndisponível",
"Instale'scikit-learn'parausarestafuncionalidade:\npipinstallscikit-learn")
return

QMessageBox.information(self,"Info","PCAemdesenvolvimento")

def_generate_stats_report(self):
"""Gerarelatórioestatísticobásico"""
ifself.dfisNone:
QMessageBox.warning(self,"Erro","Carreguedadosprimeiro!")
return

report="📈RELATÓRIOESTATÍSTICOBÁSICO\n"
report+="="*50+"\n\n"
report+=f"Arquivocarregadocom{len(self.df.columns)}colunase{len(self.df)}linhas\n\n"

forcolinself.df.columns:
ifself.df[col].dtypein['float64','int64']:
data=self.df[col].dropna()
iflen(data)>0:
report+=f"{col}:\n"
report+=f"Média:{data.mean():.4f}\n"
report+=f"Desvio:{data.std():.4f}\n"
report+=f"Min-Max:{data.min():.4f}-{data.max():.4f}\n\n"

self.stats_text.setPlainText(report)
self.info_label.setText("✅Relatórioestatísticogerado")

def_export_excel(self):
"""ExportadadosparaExcel"""
ifself.dfisNone:
QMessageBox.warning(self,"Erro","Carreguedadosprimeiro!")
return

try:
filename,_=QFileDialog.getSaveFileName(
self,"ExportarExcel","","Excelfiles(*.xlsx)"
)
iffilename:
self.df.to_excel(filename,index=False)
self.info_label.setText(f"✅Dadosexportados:{filename}")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erronaexportação:{str(e)}")

def_export_csv(self):
"""ExportadadosparaCSV"""
ifself.dfisNone:
QMessageBox.warning(self,"Erro","Carreguedadosprimeiro!")
return

try:
filename,_=QFileDialog.getSaveFileName(
self,"ExportarCSV","","CSVfiles(*.csv)"
)
iffilename:
self.df.to_csv(filename,index=False)
self.info_label.setText(f"✅Dadosexportados:{filename}")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erronaexportação:{str(e)}")

def_export_plot(self):
"""Exportagráficoatual"""
try:
filename,_=QFileDialog.getSaveFileName(
self,"ExportarGráfico","",
"PNGfiles(*.png);;PDFfiles(*.pdf);;SVGfiles(*.svg)"
)
iffilename:
self.canvas.figure.savefig(filename,dpi=300,bbox_inches='tight')
self.info_label.setText(f"✅Gráficoexportado:{filename}")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erronaexportação:{str(e)}")

#===MÉTODOSDECONTROLEDEVISUALIZAÇÃO===

def_show_fullscreen_plot(self):
"""Abregráficoemjaneladetelacheia"""
try:
#Criaremostrarjanelaemtelacheia
self.fullscreen_dialog=FullScreenPlotDialog(self,self.canvas.figure)
self.fullscreen_dialog.show()
self.info_label.setText("🔍Gráficoabertoemtelacheia-PressioneESCparafechar")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erroaoabrirtelacheia:{str(e)}")

def_refresh_plot(self):
"""Atualizaavisualizaçãodográfico"""
try:
#Redesenharcanvas
self.canvas.figure.tight_layout(pad=1.5)
self.canvas.draw()
self.info_label.setText("🔄Gráficoatualizado")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erroaoatualizar:{str(e)}")

def_zoom_fit(self):
"""Ajustazoomparamostrartodososdados"""
try:
#Auto-escalareixos
self.canvas.ax.relim()
self.canvas.ax.autoscale_view()
self.canvas.draw()
self.info_label.setText("Zoomajustadoparatodososdados")
exceptExceptionase:
QMessageBox.critical(self,"Erro",f"Erronozoom:{str(e)}")

defkeyPressEvent(self,event):
"""Teclasdeatalhoparacontrolesrápidos"""
try:
fromPySide6.QtCoreimportQt

ifevent.key()==Qt.Key_F11:
self._show_fullscreen_plot()
elifevent.key()==Qt.Key_F5:
self._refresh_plot()
elifevent.key()==Qt.Key_F:
self._zoom_fit()
else:
super().keyPressEvent(event)
except:
super().keyPressEvent(event)

def_test_plot(self):
"""Métododetesteparaverificarseográficofunciona"""
try:
#Limpargráfico
self.canvas.ax.clear()

#Criardadosdeteste
x=np.linspace(-2,2,100)
y1=np.exp(-x**2)*np.cos(5*x)#Curvatipovoltamograma
y2=0.8*np.exp(-(x-0.5)**2)*np.sin(3*x)#Segundacurva

#Plotardadosdeteste
self.canvas.ax.plot(x,y1,'o-',label='TesteAmostra1',markersize=3,alpha=0.7)
self.canvas.ax.plot(x,y2,'s-',label='TesteAmostra2',markersize=3,alpha=0.7)

#Configurargráfico
self.canvas.ax.set_xlabel('Potencial(V)',fontsize=12,fontweight='bold')
self.canvas.ax.set_ylabel('Corrente(µA)',fontsize=12,fontweight='bold')
self.canvas.ax.set_title('Teste-VoltamogramasSimulados',fontsize=14,fontweight='bold')
self.canvas.ax.grid(True,alpha=0.3)
self.canvas.ax.legend()

#Atualizarcanvas
self.canvas.figure.tight_layout()
self.canvas.draw()

self.info_label.setText("🧪Testedegráficoexecutadocomsucesso!")

exceptExceptionase:
self.info_label.setText(f"❌Erronoteste:{str(e)}")
print(f"Errodetalhadonoteste:{e}")
importtraceback
traceback.print_exc()
