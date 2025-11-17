# 🚀 CI/CD Integration Guide: Automated Drift Detection

Complete guide for integrating drift detection into your CI/CD pipeline for automated monitoring and alerts.

---

## 📋 Table of Contents

1. [GitHub Actions](#github-actions)
2. [GitLab CI](#gitlab-ci)
3. [Jenkins](#jenkins)
4. [Automated Alerts](#automated-alerts)
5. [Performance Monitoring](#performance-monitoring)

---

## 🐙 GitHub Actions

### 1. Basic Drift Detection Workflow

Create `.github/workflows/drift-detection.yml`:

```yaml
name: Data Drift Detection

on:
  push:
    branches: [ main, eze ]
  pull_request:
    branches: [ main, eze ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  drift-detection:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Pull data from DVC
        run: dvc pull

      - name: Load trained model
        run: |
          # Check if model exists, if not train it
          if [ ! -f models/best_pipeline.joblib ]; then
            echo "Training model..."
            python scripts/run_eda.py
            python scripts/run_ml.py
          fi

      - name: Simulate drift
        run: python scripts/simulate_drift.py

      - name: Detect drift
        run: python scripts/detect_drift.py

      - name: Generate visualizations
        run: python scripts/visualize_drift.py

      - name: Upload drift reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: drift-reports
          path: reports/drift/
          retention-days: 30

      - name: Upload drift visualizations
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: drift-visualizations
          path: reports/figures/10_*.png
          retention-days: 30

      - name: Parse drift report
        id: parse-report
        run: |
          python - <<'EOF'
          import json
          with open('reports/drift/drift_report.json', 'r') as f:
              report = json.load(f)

          critical_alerts = report['alerts'].__len__([a for a in report.get('alerts', []) if a.get('level') == 'critical'])
          warning_alerts = report['alerts'].__len__([a for a in report.get('alerts', []) if a.get('level') == 'warning'])

          print(f"::set-output name=critical::{critical_alerts}")
          print(f"::set-output name=warnings::{warning_alerts}")
          EOF

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('reports/drift/drift_report.json', 'utf8'));

            const summary = report.summary;
            const comment = `
            ## 📊 Drift Detection Results

            - **Features Analyzed**: ${summary.total_features_analyzed}
            - **Features with Drift**: ${summary.features_with_drift}
            - **Critical Alerts**: ${summary.critical_alerts}
            - **Warning Alerts**: ${summary.warning_alerts}

            **Baseline Accuracy**: ${(report.baseline_metrics.accuracy * 100).toFixed(2)}%
            **Current Accuracy**: ${(report.current_metrics.accuracy * 100).toFixed(2)}%
            **Degradation**: ${(((report.baseline_metrics.accuracy - report.current_metrics.accuracy) / report.baseline_metrics.accuracy) * 100).toFixed(2)}%
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail if critical alerts
        run: |
          if [ ${{ steps.parse-report.outputs.critical }} -gt 0 ]; then
            echo "❌ Critical drift detected!"
            exit 1
          fi
```

---

### 2. Multi-Branch Testing Workflow

Create `.github/workflows/drift-matrix.yml`:

```yaml
name: Drift Detection Matrix Tests

on: [push, pull_request]

jobs:
  test-drift:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11']
      fail-fast: false

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run drift detection tests
        run: pytest tests/test_drift_detection.py -v --cov=src/monitoring --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

---

### 3. Scheduled Weekly Report Workflow

Create `.github/workflows/weekly-drift-report.yml`:

```yaml
name: Weekly Drift Report

on:
  schedule:
    # Every Monday at 8 AM UTC
    - cron: '0 8 * * MON'
  workflow_dispatch:

jobs:
  weekly-report:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pandas matplotlib seaborn

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Generate comprehensive report
        run: |
          python - <<'EOF'
          import json
          from datetime import datetime
          import pandas as pd

          # Load latest report
          with open('reports/drift/drift_report.json', 'r') as f:
              report = json.load(f)

          # Generate summary
          summary = f"""
          # Weekly Drift Detection Report
          Generated: {datetime.now().isoformat()}

          ## Summary
          - Total Features: {report['summary']['total_features_analyzed']}
          - Features with Drift: {report['summary']['features_with_drift']}
          - Critical Alerts: {report['summary']['critical_alerts']}
          - Warning Alerts: {report['summary']['warning_alerts']}

          ## Performance Impact
          - Baseline Accuracy: {report['baseline_metrics']['accuracy']:.4f}
          - Current Accuracy: {report['current_metrics']['accuracy']:.4f}
          - Degradation: {((report['baseline_metrics']['accuracy'] - report['current_metrics']['accuracy']) / report['baseline_metrics']['accuracy'] * 100):.2f}%

          ## Feature Drift Details
          """

          for feature, metrics in report['feature_drift'].items():
              summary += f"\n### {feature}\n"
              summary += f"- PSI: {metrics.get('psi', 'N/A')}\n"
              summary += f"- Mean Shift: {metrics.get('mean_shift_pct', 'N/A'):.2f}%\n"
              summary += f"- Severity: {metrics.get('drift_severity', 'N/A')}\n"

          with open('WEEKLY_DRIFT_REPORT.md', 'w') as f:
              f.write(summary)

          print("Report generated successfully")
          EOF

      - name: Create GitHub Issue with report
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('WEEKLY_DRIFT_REPORT.md', 'utf8');

            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `📊 Weekly Drift Report - ${new Date().toLocaleDateString()}`,
              body: report,
              labels: ['monitoring', 'drift-detection']
            });

      - name: Send Slack notification
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Weekly drift detection report failed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          fields: repo,message,commit
```

---

## 🦊 GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - drift-detection
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

test-drift-detection:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - pytest tests/test_drift_detection.py -v --cov=src/monitoring --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

simulate-and-detect-drift:
  stage: drift-detection
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python scripts/simulate_drift.py
    - python scripts/detect_drift.py
    - python scripts/visualize_drift.py
  artifacts:
    paths:
      - reports/drift/
      - reports/figures/10_*.png
    expire_in: 30 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == "main"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request"'

generate-drift-report:
  stage: report
  image: python:3.10
  script:
    - pip install -r requirements.txt pandas
    - python scripts/generate_drift_report.py
  artifacts:
    paths:
      - DRIFT_REPORT.md
    reports:
      metrics: drift_metrics.json
  needs: ["simulate-and-detect-drift"]
  only:
    - main
    - merge_requests
```

---

## 🔧 Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        VENV_DIR = "${WORKSPACE}/.venv"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
    }

    triggers {
        // Run on push to main/develop
        githubPush()

        // Run daily at 2 AM
        cron('0 2 * * *')
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    sh '''
                        python${PYTHON_VERSION} -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_drift_detection.py -v --junitxml=test-results.xml --cov=src/monitoring --cov-report=html
                    '''
                }
            }
        }

        stage('Drift Simulation') {
            steps {
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        python scripts/simulate_drift.py
                    '''
                }
            }
        }

        stage('Drift Detection') {
            steps {
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        python scripts/detect_drift.py
                    '''
                }
            }
        }

        stage('Generate Visualizations') {
            steps {
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        python scripts/visualize_drift.py
                    '''
                }
            }
        }

        stage('Archive Results') {
            when {
                always()
            }
            steps {
                archiveArtifacts artifacts: 'reports/drift/**', allowEmptyArchive: true
                archiveArtifacts artifacts: 'reports/figures/10_*.png,reports/figures/11_*.png,reports/figures/12_*.png', allowEmptyArchive: true
                junit 'test-results.xml'
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }

        stage('Notify') {
            when {
                always()
            }
            steps {
                script {
                    if (currentBuild.result == 'FAILURE') {
                        // Send Slack notification
                        sh '''
                            curl -X POST $SLACK_WEBHOOK -H 'Content-type: application/json' \
                            --data '{"text":"🚨 Drift detection failed for build ${BUILD_NUMBER}"}'
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

---

## 🔔 Automated Alerts

### 1. Slack Integration

Create `scripts/send_slack_alert.py`:

```python
"""
Send drift detection alerts to Slack
"""

import json
import requests
from pathlib import Path
from typing import Dict

def send_slack_alert(report_path: Path, webhook_url: str):
    """
    Send drift detection results to Slack

    Args:
        report_path: Path to drift_report.json
        webhook_url: Slack webhook URL
    """
    with open(report_path, 'r') as f:
        report = json.load(f)

    summary = report['summary']

    # Determine color based on severity
    if summary['critical_alerts'] > 0:
        color = 'danger'  # Red
        emoji = '🚨'
    elif summary['warning_alerts'] > 0:
        color = 'warning'  # Orange
        emoji = '⚠️'
    else:
        color = 'good'  # Green
        emoji = '✅'

    # Build message
    message = {
        "attachments": [
            {
                "color": color,
                "title": f"{emoji} Data Drift Detection Report",
                "fields": [
                    {
                        "title": "Features Analyzed",
                        "value": str(summary['total_features_analyzed']),
                        "short": True
                    },
                    {
                        "title": "Features with Drift",
                        "value": str(summary['features_with_drift']),
                        "short": True
                    },
                    {
                        "title": "Critical Alerts",
                        "value": str(summary['critical_alerts']),
                        "short": True
                    },
                    {
                        "title": "Warning Alerts",
                        "value": str(summary['warning_alerts']),
                        "short": True
                    },
                    {
                        "title": "Baseline Accuracy",
                        "value": f"{report['baseline_metrics']['accuracy']:.4f}",
                        "short": True
                    },
                    {
                        "title": "Current Accuracy",
                        "value": f"{report['current_metrics']['accuracy']:.4f}",
                        "short": True
                    }
                ]
            }
        ]
    }

    # Send to Slack
    response = requests.post(webhook_url, json=message)
    response.raise_for_status()
    print("Alert sent to Slack successfully")

if __name__ == "__main__":
    import sys

    report_path = Path("reports/drift/drift_report.json")
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SLACK_WEBHOOK")

    send_slack_alert(report_path, webhook_url)
```

Use in CI/CD:
```bash
python scripts/send_slack_alert.py $SLACK_WEBHOOK_URL
```

---

### 2. Email Alerts

Create `scripts/send_email_alert.py`:

```python
"""
Send drift detection alerts via email
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List

def send_email_alert(
    report_path: Path,
    smtp_server: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: List[str]
):
    """
    Send drift detection results via email
    """
    with open(report_path, 'r') as f:
        report = json.load(f)

    summary = report['summary']

    # Build HTML email
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #333; }}
            .critical {{ color: red; font-weight: bold; }}
            .warning {{ color: orange; font-weight: bold; }}
            .success {{ color: green; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>📊 Data Drift Detection Report</h1>

        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Features Analyzed</td>
                <td>{summary['total_features_analyzed']}</td>
            </tr>
            <tr>
                <td>Features with Drift</td>
                <td>{summary['features_with_drift']}</td>
            </tr>
            <tr>
                <td class="critical">Critical Alerts</td>
                <td class="critical">{summary['critical_alerts']}</td>
            </tr>
            <tr>
                <td class="warning">Warning Alerts</td>
                <td class="warning">{summary['warning_alerts']}</td>
            </tr>
        </table>

        <h2>Performance Impact</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Baseline</th>
                <th>Current</th>
                <th>Degradation</th>
            </tr>
            <tr>
                <td>Accuracy</td>
                <td>{report['baseline_metrics']['accuracy']:.4f}</td>
                <td>{report['current_metrics']['accuracy']:.4f}</td>
                <td>{((report['baseline_metrics']['accuracy'] - report['current_metrics']['accuracy']) / report['baseline_metrics']['accuracy'] * 100):.2f}%</td>
            </tr>
        </table>
    </body>
    </html>
    """

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🚨 Drift Detection Alert - {summary['critical_alerts']} Critical Issues"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    msg.attach(MIMEText(html, 'html'))

    # Send email
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(sender, password)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

    print(f"Alert sent to {len(recipients)} recipients")
```

---

## 📈 Performance Monitoring

### Integration with Datadog

Create `scripts/send_metrics_to_datadog.py`:

```python
"""
Send drift metrics to Datadog for monitoring
"""

from datadog import initialize, api
from pathlib import Path
import json
from datetime import datetime

def send_to_datadog(report_path: Path, api_key: str, app_key: str):
    """
    Send drift metrics to Datadog
    """
    options = {
        'api_key': api_key,
        'app_key': app_key
    }
    initialize(**options)

    with open(report_path, 'r') as f:
        report = json.load(f)

    now = int(datetime.now().timestamp())
    summary = report['summary']

    # Send metrics
    metrics_data = [
        {
            'metric': 'drift.features_with_drift',
            'points': [(now, summary['features_with_drift'])],
            'type': 'gauge'
        },
        {
            'metric': 'drift.critical_alerts',
            'points': [(now, summary['critical_alerts'])],
            'type': 'gauge'
        },
        {
            'metric': 'drift.warning_alerts',
            'points': [(now, summary['warning_alerts'])],
            'type': 'gauge'
        },
        {
            'metric': 'model.accuracy',
            'points': [(now, report['current_metrics']['accuracy'])],
            'type': 'gauge'
        }
    ]

    for metric_data in metrics_data:
        api.Metric.send(**metric_data)

    print("Metrics sent to Datadog successfully")
```

---

## 📊 Summary: CI/CD Setup Checklist

- [ ] GitHub Actions workflows created (.github/workflows/)
- [ ] Secrets configured (AWS, Slack, etc.)
- [ ] Test coverage threshold set (e.g., 80%)
- [ ] Slack/Email alerts configured
- [ ] Datadog/monitoring integration done
- [ ] Build notifications enabled
- [ ] PR comments with drift results enabled
- [ ] Weekly report scheduled
- [ ] Artifact retention policies set
- [ ] Emergency escalation procedures documented

---

**CI/CD integration complete!** 🎉

Drift detection is now automatically tested and monitored on every push and daily schedule.
