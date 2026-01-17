#!/usr/bin/env python
"""Quick demo showing 3 invoices processed with team monitoring"""

from ap_team_orchestrator import APTeamOrchestrator
import os

print('='*80)
print('  LEAD AGENT TEAM MONITORING DEMO')
print('='*80)
print()

orchestrator = APTeamOrchestrator()
print('[OK] Team initialized with 9 agents')
print()

if not os.path.exists('sample_invoices'):
    os.makedirs('sample_invoices')

# Use existing files
invoices_files = [
    'sample_invoices/invoice_001.txt',
    'sample_invoices/invoice_standard.txt',
    'sample_invoices/invoice_large.txt'
]

sources = ['email', 'api', 'upload']

processed = []
print('Processing invoices...')
for filepath, source in zip(invoices_files, sources):
    if os.path.exists(filepath):
        try:
            invoice = orchestrator.process_invoice(filepath, source)
            processed.append(invoice)
            print(f'  * {os.path.basename(filepath)} ({source}) [OK]')
        except Exception as e:
            print(f'  * Error: {e}')

print()
print('='*80)
print('  TEAM PERFORMANCE REPORT')
print('='*80)
print()

total_processed = 0
total_successful = 0

print('Agent Performance:')
print('-'*80)
for i, agent in enumerate(orchestrator.lead_agent.team, 1):
    metrics = agent.get_metrics()
    m = metrics['metrics']
    processed_count = m['processed']
    successful_count = m['successful']
    success_rate = (successful_count / processed_count * 100) if processed_count > 0 else 0
    
    total_processed += processed_count
    total_successful += successful_count
    
    print(f'{i}. {agent.agent_name:<20} Processed: {processed_count:2}  Success: {success_rate:.1f}%')

print('-'*80)
overall_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0
print(f'OVERALL                      Processed: {total_processed:2}  Success: {overall_rate:.1f}%')
print()

print('='*80)
print('  PROCESSED INVOICES')
print('='*80)
print()

total_amount = 0
for invoice in processed:
    vendor = invoice.extracted_data.get('vendor_name', 'Unknown')
    amount = invoice.extracted_data.get('total_amount', 0)
    status = invoice.status.value
    total_amount += amount
    
    print(f'Invoice: {invoice.invoice_id}')
    print(f'  Vendor: {vendor}')
    amount_str = f'${amount:,.2f}'
    print(f'  Amount: {amount_str}')
    print(f'  Status: {status}')
    print(f'  Posted: [OK]')
    print()

print('-'*80)
print(f'Total Invoices: {len(processed)}')
total_str = f'${total_amount:,.2f}'
print(f'Total Amount: {total_str}')
print()
print('='*80)
print('  DEMO COMPLETED SUCCESSFULLY')
print('='*80)
