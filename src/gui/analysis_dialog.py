from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QLabel, QTextEdit, QPushButton, QComboBox,
                           QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog,
                           QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.core.vulnerability_analyzer import VulnerabilityAnalyzer, RiskLevel
from typing import Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class AnalysisDialog(QDialog):
    def __init__(self, scan_result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("扫描结果分析")
        self.resize(1000, 800)
        
        self.scan_result = scan_result
        self.analyzer = VulnerabilityAnalyzer()
        self.vulnerabilities = self.analyzer.analyze_vulnerability(scan_result)
        
        self.setup_ui()
        self.analyze_results()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 漏洞概览选项卡
        overview_tab = self._create_overview_tab()
        tab_widget.addTab(overview_tab, "漏洞概览")
        
        # 详细分析选项卡
        analysis_tab = self._create_analysis_tab()
        tab_widget.addTab(analysis_tab, "详细分析")
        
        # 修复建议选项卡
        remediation_tab = self._create_remediation_tab()
        tab_widget.addTab(remediation_tab, "修复建议")
        
        # 结果对比选项卡
        comparison_tab = self._create_comparison_tab()
        tab_widget.addTab(comparison_tab, "结果对比")
        
        # 漏洞评估选项卡
        assessment_tab = self._create_assessment_tab()
        tab_widget.addTab(assessment_tab, "漏洞评估")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton("导出报告")
        button_layout.addWidget(self.export_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.export_btn.clicked.connect(self.export_report)
        
    def _create_overview_tab(self) -> QWidget:
        """创建漏洞概览选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 统计图表
        figure, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        
        # 风险等级分布饼图
        risk_stats = self._get_risk_statistics()
        if risk_stats['total'] > 0:
            labels = []
            sizes = []
            colors = []
            for level in RiskLevel:
                count = risk_stats[level]
                if count > 0:
                    labels.append(f"{level.value} ({count})")
                    sizes.append(count)
                    if level == RiskLevel.CRITICAL:
                        colors.append('red')
                    elif level == RiskLevel.HIGH:
                        colors.append('orange')
                    elif level == RiskLevel.MEDIUM:
                        colors.append('yellow')
                    elif level == RiskLevel.LOW:
                        colors.append('blue')
                    else:
                        colors.append('gray')
                        
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
            ax1.set_title("漏洞风险等级分布")
            
        # 漏洞类型统计柱状图
        type_stats = self._get_vulnerability_types()
        if type_stats:
            types = list(type_stats.keys())
            counts = list(type_stats.values())
            ax2.bar(types, counts)
            ax2.set_title("漏洞类型统计")
            plt.xticks(rotation=45)
            
        canvas = FigureCanvasQTAgg(figure)
        layout.addWidget(canvas)
        
        # 统计信息
        stats_text = f"""
        扫描结果��计:
        - 总计发现 {risk_stats['total']} 个漏洞
        - 严重级别: {risk_stats[RiskLevel.CRITICAL]} 个
        - 高危级别: {risk_stats[RiskLevel.HIGH]} 个
        - 中危级别: {risk_stats[RiskLevel.MEDIUM]} 个
        - 低危级别: {risk_stats[RiskLevel.LOW]} 个
        - 信息级别: {risk_stats[RiskLevel.INFO]} 个
        """
        stats_label = QLabel(stats_text)
        layout.addWidget(stats_label)
        
        widget.setLayout(layout)
        return widget
        
    def _create_analysis_tab(self) -> QWidget:
        """创建详细分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 漏洞树
        self.vuln_tree = QTreeWidget()
        self.vuln_tree.setHeaderLabels(["漏洞", "风险等级", "描述"])
        self.vuln_tree.setColumnWidth(0, 200)
        self.vuln_tree.setColumnWidth(1, 100)
        
        for vuln in self.vulnerabilities:
            item = QTreeWidgetItem([
                vuln.type,
                vuln.risk_level.value,
                vuln.description
            ])
            
            # 设置风险等级的颜色
            if vuln.risk_level == RiskLevel.CRITICAL:
                item.setBackground(1, QColor(255, 0, 0, 100))
            elif vuln.risk_level == RiskLevel.HIGH:
                item.setBackground(1, QColor(255, 165, 0, 100))
            elif vuln.risk_level == RiskLevel.MEDIUM:
                item.setBackground(1, QColor(255, 255, 0, 100))
            elif vuln.risk_level == RiskLevel.LOW:
                item.setBackground(1, QColor(0, 0, 255, 100))
                
            # 添加详细信息
            impact_item = QTreeWidgetItem(["影响", "", vuln.impact])
            item.addChild(impact_item)
            
            if vuln.references:
                ref_item = QTreeWidgetItem(["参考", "", ""])
                for ref in vuln.references:
                    ref_item.addChild(QTreeWidgetItem(["", "", ref]))
                item.addChild(ref_item)
                
            self.vuln_tree.addTopLevelItem(item)
            
        layout.addWidget(self.vuln_tree)
        
        widget.setLayout(layout)
        return widget
        
    def _create_remediation_tab(self) -> QWidget:
        """创建修复建议选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 漏洞选择
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("选择漏洞:"))
        self.vuln_combo = QComboBox()
        self.vuln_combo.addItems([v.type for v in self.vulnerabilities])
        selection_layout.addWidget(self.vuln_combo)
        layout.addLayout(selection_layout)
        
        # 修复建议显示
        self.remediation_text = QTextEdit()
        self.remediation_text.setReadOnly(True)
        layout.addWidget(self.remediation_text)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.vuln_combo.currentTextChanged.connect(self._update_remediation)
        if self.vulnerabilities:
            self._update_remediation(self.vulnerabilities[0].type)
            
        return widget
        
    def _create_comparison_tab(self) -> QWidget:
        """创建结果对比选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 选择要对比的结果
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("选择对比结果:"))
        self.result_combo = QComboBox()
        # TODO: 从历史记录中加载可用的扫描结果
        selection_layout.addWidget(self.result_combo)
        self.compare_btn = QPushButton("对比")
        selection_layout.addWidget(self.compare_btn)
        layout.addLayout(selection_layout)
        
        # 对比结果显示
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        layout.addWidget(self.comparison_text)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.compare_btn.clicked.connect(self._compare_results)
        
        return widget
        
    def _create_assessment_tab(self) -> QWidget:
        """创建漏洞评估选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 漏洞列表
        vuln_list = QTreeWidget()
        vuln_list.setHeaderLabels([
            "ID", "漏洞名称", "风险等级", "CVSS分数", "状态"
        ])
        vuln_list.setColumnWidth(0, 100)
        vuln_list.setColumnWidth(1, 200)
        vuln_list.setColumnWidth(2, 100)
        vuln_list.setColumnWidth(3, 100)
        
        # 添加漏洞
        for vuln in self.vulnerabilities:
            item = QTreeWidgetItem([
                vuln.id,
                vuln.name,
                vuln.risk_level.value,
                f"{vuln.cvss_score:.1f}",
                "未修复"
            ])
            
            # 设置风险等级颜色
            if vuln.risk_level == RiskLevel.CRITICAL:
                item.setBackground(2, QColor(255, 0, 0, 100))
            elif vuln.risk_level == RiskLevel.HIGH:
                item.setBackground(2, QColor(255, 165, 0, 100))
            elif vuln.risk_level == RiskLevel.MEDIUM:
                item.setBackground(2, QColor(255, 255, 0, 100))
            elif vuln.risk_level == RiskLevel.LOW:
                item.setBackground(2, QColor(0, 0, 255, 100))
                
            vuln_list.addTopLevelItem(item)
            
        layout.addWidget(vuln_list)
        
        # 详细信息
        detail_group = QGroupBox("漏洞详情")
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        # 连接信号
        vuln_list.currentItemChanged.connect(self._show_vuln_detail)
        
        widget.setLayout(layout)
        return widget
        
    def _show_vuln_detail(self, current, previous):
        """显示漏洞详情"""
        if not current:
            return
            
        vuln_id = current.text(0)
        vuln = next((v for v in self.vulnerabilities if v.id == vuln_id), None)
        if not vuln:
            return
            
        detail = f"""
        <h2>{vuln.name}</h2>
        <p><b>风险等级:</b> {vuln.risk_level.value}</p>
        <p><b>CVSS分数:</b> {vuln.cvss_score:.1f}</p>
        
        <h3>漏洞描述</h3>
        <p>{vuln.description}</p>
        
        <h3>影响评估</h3>
        <ul>
            <li>机密性影响: {vuln.impact.confidentiality:.1f}</li>
            <li>完整性影响: {vuln.impact.integrity:.1f}</li>
            <li>可用性影响: {vuln.impact.availability:.1f}</li>
            <li>影响范围: {vuln.impact.scope:.1f}</li>
        </ul>
        
        <h3>攻击指标</h3>
        <ul>
            <li>攻击向量复杂度: {vuln.metrics.attack_vector:.1f}</li>
            <li>攻击复杂度: {vuln.metrics.attack_complexity:.1f}</li>
            <li>所需权限: {vuln.metrics.privileges_required:.1f}</li>
            <li>用户交互: {vuln.metrics.user_interaction:.1f}</li>
            <li>利用成熟度: {vuln.metrics.exploit_maturity:.1f}</li>
        </ul>
        
        <h3>受影响的URL</h3>
        <ul>
        """
        
        for url in vuln.affected_urls:
            detail += f"<li>{url}</li>"
            
        detail += """
        </ul>
        
        <h3>修复建议</h3>
        <ul>
        """
        
        for fix in vuln.remediation:
            detail += f"<li>{fix}</li>"
            
        detail += """
        </ul>
        
        <h3>参考链接</h3>
        <ul>
        """
        
        for ref in vuln.references:
            detail += f'<li><a href="{ref}">{ref}</a></li>'
            
        detail += "</ul>"
        
        self.detail_text.setHtml(detail)
        
    def _get_risk_statistics(self) -> Dict:
        """获取风险等级统计"""
        stats = {level: 0 for level in RiskLevel}
        stats['total'] = len(self.vulnerabilities)
        
        for vuln in self.vulnerabilities:
            stats[vuln.risk_level] += 1
            
        return stats
        
    def _get_vulnerability_types(self) -> Dict:
        """获取漏洞类型统计"""
        types = {}
        for vuln in self.vulnerabilities:
            if vuln.type not in types:
                types[vuln.type] = 0
            types[vuln.type] += 1
        return types
        
    def _update_remediation(self, vuln_type: str):
        """更新修复建议"""
        for vuln in self.vulnerabilities:
            if vuln.type == vuln_type:
                self.remediation_text.setText(vuln.remediation)
                break
                
    def _compare_results(self):
        """比较扫描结果"""
        # TODO: 实现结果对比功能
        selected_result = self.result_combo.currentData()
        if not selected_result:
            return
            
        comparison = self.analyzer.compare_results(selected_result, self.scan_result)
        
        report = ["# 扫描结果对比\n"]
        
        if comparison['new_vulnerabilities']:
            report.append("\n## 新增漏洞")
            for vuln in comparison['new_vulnerabilities']:
                report.append(f"- {vuln['type']}: {vuln['details']}")
                
        if comparison['fixed_vulnerabilities']:
            report.append("\n## 已修复漏洞")
            for vuln in comparison['fixed_vulnerabilities']:
                report.append(f"- {vuln['type']}: {vuln['details']}")
                
        if comparison['unchanged_vulnerabilities']:
            report.append("\n## 未修复漏洞")
            for vuln in comparison['unchanged_vulnerabilities']:
                report.append(f"- {vuln['type']}: {vuln['details']}")
                
        self.comparison_text.setText("\n".join(report))
        
    def analyze_results(self):
        """分析扫描结果"""
        if not self.vulnerabilities:
            QMessageBox.information(self, "提示", "未发现漏洞")
            
    def export_report(self):
        """导出分析报告"""
        report = self.analyzer.generate_report(self.vulnerabilities)
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出报告", "", "Markdown文件 (*.md)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                QMessageBox.information(self, "成功", "报告已导出")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}") 