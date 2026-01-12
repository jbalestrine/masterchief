"""
Script Scheduler
Cron-based automated script execution
"""

import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import subprocess
import time

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    """Represents a scheduled job."""
    id: str
    script_name: str
    cron: str
    args: List[str]
    notify: bool
    timezone: str
    enabled: bool
    created_at: str
    last_run: Optional[str] = None
    next_run: Optional[str] = None


@dataclass
class ExecutionRecord:
    """Represents a script execution record."""
    id: Optional[int]
    script_name: str
    started_at: str
    finished_at: Optional[str]
    return_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    execution_time: Optional[float]
    success: bool


class ScheduleDatabase:
    """Database for storing schedule and execution history."""
    
    def __init__(self, db_path: Path):
        """
        Initialize schedule database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                script_name TEXT NOT NULL,
                cron TEXT NOT NULL,
                args TEXT,
                notify INTEGER DEFAULT 0,
                timezone TEXT DEFAULT 'UTC',
                enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_run TEXT,
                next_run TEXT
            )
        """)
        
        # Create execution history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                return_code INTEGER,
                stdout TEXT,
                stderr TEXT,
                execution_time REAL,
                success INTEGER DEFAULT 0,
                INDEX idx_script_name (script_name),
                INDEX idx_started_at (started_at)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_schedule(self, job: ScheduledJob) -> bool:
        """Save a scheduled job."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO schedules 
                (id, script_name, cron, args, notify, timezone, enabled, created_at, last_run, next_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.script_name,
                job.cron,
                json.dumps(job.args),
                1 if job.notify else 0,
                job.timezone,
                1 if job.enabled else 0,
                job.created_at,
                job.last_run,
                job.next_run
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save schedule: {e}")
            return False
    
    def get_schedule(self, job_id: str) -> Optional[ScheduledJob]:
        """Get a scheduled job by ID."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM schedules WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return ScheduledJob(
                    id=row['id'],
                    script_name=row['script_name'],
                    cron=row['cron'],
                    args=json.loads(row['args']),
                    notify=bool(row['notify']),
                    timezone=row['timezone'],
                    enabled=bool(row['enabled']),
                    created_at=row['created_at'],
                    last_run=row['last_run'],
                    next_run=row['next_run']
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get schedule: {e}")
            return None
    
    def list_schedules(self) -> List[ScheduledJob]:
        """List all scheduled jobs."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM schedules ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            jobs = []
            for row in rows:
                jobs.append(ScheduledJob(
                    id=row['id'],
                    script_name=row['script_name'],
                    cron=row['cron'],
                    args=json.loads(row['args']),
                    notify=bool(row['notify']),
                    timezone=row['timezone'],
                    enabled=bool(row['enabled']),
                    created_at=row['created_at'],
                    last_run=row['last_run'],
                    next_run=row['next_run']
                ))
            return jobs
        except Exception as e:
            logger.error(f"Failed to list schedules: {e}")
            return []
    
    def delete_schedule(self, job_id: str) -> bool:
        """Delete a scheduled job."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedules WHERE id = ?", (job_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete schedule: {e}")
            return False
    
    def save_execution(self, record: ExecutionRecord) -> bool:
        """Save an execution record."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO executions 
                (script_name, started_at, finished_at, return_code, stdout, stderr, execution_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.script_name,
                record.started_at,
                record.finished_at,
                record.return_code,
                record.stdout,
                record.stderr,
                record.execution_time,
                1 if record.success else 0
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save execution record: {e}")
            return False
    
    def get_history(self, script_name: Optional[str] = None, limit: int = 100) -> List[ExecutionRecord]:
        """Get execution history."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if script_name:
                cursor.execute(
                    "SELECT * FROM executions WHERE script_name = ? ORDER BY started_at DESC LIMIT ?",
                    (script_name, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM executions ORDER BY started_at DESC LIMIT ?",
                    (limit,)
                )
            
            rows = cursor.fetchall()
            conn.close()
            
            records = []
            for row in rows:
                records.append(ExecutionRecord(
                    id=row['id'],
                    script_name=row['script_name'],
                    started_at=row['started_at'],
                    finished_at=row['finished_at'],
                    return_code=row['return_code'],
                    stdout=row['stdout'],
                    stderr=row['stderr'],
                    execution_time=row['execution_time'],
                    success=bool(row['success'])
                ))
            return records
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []


class ScriptScheduler:
    """Cron-based script scheduling."""
    
    def __init__(self, scripts_dir: Path, db_path: Path, notification_callback=None):
        """
        Initialize script scheduler.
        
        Args:
            scripts_dir: Directory containing scripts
            db_path: Path to schedule database
            notification_callback: Optional callback for notifications
        """
        self.scripts_dir = Path(scripts_dir)
        self.db = ScheduleDatabase(db_path)
        self.notification_callback = notification_callback
        
        # Initialize APScheduler
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{db_path}')
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()
        
        # Restore scheduled jobs from database
        self._restore_jobs()
    
    def _restore_jobs(self):
        """Restore scheduled jobs from database on startup."""
        jobs = self.db.list_schedules()
        for job in jobs:
            if job.enabled:
                try:
                    self._schedule_job(job)
                    logger.info(f"Restored scheduled job: {job.script_name}")
                except Exception as e:
                    logger.error(f"Failed to restore job {job.script_name}: {e}")
    
    def _schedule_job(self, job: ScheduledJob):
        """Internal method to schedule a job with APScheduler."""
        trigger = CronTrigger.from_crontab(job.cron, timezone=job.timezone)
        
        self.scheduler.add_job(
            func=self._execute_script,
            trigger=trigger,
            args=[job],
            id=job.id,
            replace_existing=True
        )
    
    def _execute_script(self, job: ScheduledJob):
        """Execute a scheduled script."""
        script_path = self.scripts_dir / job.script_name
        
        if not script_path.exists():
            logger.error(f"Scheduled script not found: {job.script_name}")
            return
        
        logger.info(f"Executing scheduled script: {job.script_name}")
        
        # Create execution record
        started_at = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            # Execute script
            cmd = [str(script_path)]
            if job.args:
                cmd.extend(job.args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            execution_time = time.time() - start_time
            finished_at = datetime.now().isoformat()
            
            # Save execution record
            record = ExecutionRecord(
                id=None,
                script_name=job.script_name,
                started_at=started_at,
                finished_at=finished_at,
                return_code=result.returncode,
                stdout=result.stdout[:10000] if result.stdout else None,  # Limit size
                stderr=result.stderr[:10000] if result.stderr else None,
                execution_time=execution_time,
                success=result.returncode == 0
            )
            
            self.db.save_execution(record)
            
            # Send notification if enabled
            if job.notify and self.notification_callback:
                status = "✓ Success" if result.returncode == 0 else "✗ Failed"
                message = f"Scheduled script {job.script_name}: {status}"
                self.notification_callback(message, record)
            
            # Update last run time
            job.last_run = finished_at
            self.db.save_schedule(job)
            
            logger.info(f"Script {job.script_name} completed with return code {result.returncode}")
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script {job.script_name} timed out")
            execution_time = time.time() - start_time
            
            record = ExecutionRecord(
                id=None,
                script_name=job.script_name,
                started_at=started_at,
                finished_at=datetime.now().isoformat(),
                return_code=-1,
                stdout=None,
                stderr="Script execution timed out",
                execution_time=execution_time,
                success=False
            )
            self.db.save_execution(record)
            
        except Exception as e:
            logger.error(f"Failed to execute script {job.script_name}: {e}")
            
            record = ExecutionRecord(
                id=None,
                script_name=job.script_name,
                started_at=started_at,
                finished_at=datetime.now().isoformat(),
                return_code=-1,
                stdout=None,
                stderr=str(e),
                execution_time=time.time() - start_time,
                success=False
            )
            self.db.save_execution(record)
    
    def add(
        self,
        script_name: str,
        cron: str,
        args: List[str] = None,
        notify: bool = False,
        timezone: str = "UTC"
    ) -> Optional[ScheduledJob]:
        """
        Schedule a script for recurring execution.
        
        Args:
            script_name: Name of the script to schedule
            cron: Cron expression
            args: Optional command line arguments
            notify: Whether to send notifications
            timezone: Timezone for scheduling
            
        Returns:
            ScheduledJob object or None if failed
        """
        try:
            # Validate script exists
            script_path = self.scripts_dir / script_name
            if not script_path.exists():
                logger.error(f"Script not found: {script_name}")
                return None
            
            # Create job
            job_id = f"script_{script_name}_{int(time.time())}"
            job = ScheduledJob(
                id=job_id,
                script_name=script_name,
                cron=cron,
                args=args or [],
                notify=notify,
                timezone=timezone,
                enabled=True,
                created_at=datetime.now().isoformat()
            )
            
            # Save to database
            if not self.db.save_schedule(job):
                return None
            
            # Schedule with APScheduler
            self._schedule_job(job)
            
            logger.info(f"Scheduled script {script_name} with cron: {cron}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to schedule script: {e}")
            return None
    
    def remove(self, script_name: str) -> bool:
        """
        Remove a scheduled script.
        
        Args:
            script_name: Name of the script
            
        Returns:
            True if removed successfully
        """
        try:
            # Find jobs for this script
            jobs = self.db.list_schedules()
            removed = False
            
            for job in jobs:
                if job.script_name == script_name:
                    # Remove from scheduler
                    try:
                        self.scheduler.remove_job(job.id)
                    except:
                        pass
                    
                    # Remove from database
                    self.db.delete_schedule(job.id)
                    removed = True
            
            return removed
            
        except Exception as e:
            logger.error(f"Failed to remove schedule: {e}")
            return False
    
    def list_jobs(self) -> List[ScheduledJob]:
        """List all scheduled jobs."""
        return self.db.list_schedules()
    
    def get_history(self, script_name: Optional[str] = None, limit: int = 100) -> List[ExecutionRecord]:
        """Get execution history."""
        return self.db.get_history(script_name, limit)
    
    def pause(self, script_name: str) -> bool:
        """Pause a scheduled job."""
        try:
            jobs = self.db.list_schedules()
            for job in jobs:
                if job.script_name == script_name and job.enabled:
                    # Pause in scheduler
                    self.scheduler.pause_job(job.id)
                    
                    # Update database
                    job.enabled = False
                    self.db.save_schedule(job)
                    
                    logger.info(f"Paused job: {script_name}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to pause job: {e}")
            return False
    
    def resume(self, script_name: str) -> bool:
        """Resume a paused job."""
        try:
            jobs = self.db.list_schedules()
            for job in jobs:
                if job.script_name == script_name and not job.enabled:
                    # Resume in scheduler
                    self.scheduler.resume_job(job.id)
                    
                    # Update database
                    job.enabled = True
                    self.db.save_schedule(job)
                    
                    logger.info(f"Resumed job: {script_name}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume job: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
