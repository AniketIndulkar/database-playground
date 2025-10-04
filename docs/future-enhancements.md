# Advanced Object Storage Features

This document outlines advanced features and best practices for object storage that can be implemented as you deepen your understanding.

## 🎯 Current Implementation Status

✅ **Implemented:**
- Basic upload/download operations
- Bucket creation and management
- File listing
- Direct key-based access

⏳ **Future Enhancements:**
- Versioning strategies
- Immutable storage patterns
- Advanced naming conventions
- Performance optimization

---

## 1. Versioning - Keep All Versions

**Use Case:** When you need a complete history of changes (like Git for files)

**Examples:**
- Document management systems
- Compliance and audit requirements
- Backup and recovery scenarios

### Implementation Approaches

#### A. MinIO Built-in Versioning
MinIO supports S3-compatible versioning out of the box:

```python
# Enable versioning on bucket
self.client.set_bucket_versioning(
    bucket_name=self.bucket_name,
    config=VersioningConfig(ENABLED)
)

# All uploads automatically create new versions
# Old versions are preserved with version IDs
```

**Pros:** Automatic, reliable, industry-standard
**Cons:** Increases storage costs, requires version management

#### B. Application-Level Versioning
Store version metadata in the object name or metadata:

```python
def upload_with_version(self, file_path: str, base_name: str):
    # Get current version count
    version = self._get_next_version(base_name)
    object_name = f"{base_name}_v{version}"
    return self.upload_file(file_path, object_name)
```

**Pros:** More control, can implement custom logic
**Cons:** Manual management, more complex queries

---

## 2. Immutable Storage - Write Once, Read Many (WORM)

**Use Case:** When data must never be modified or deleted

**Examples:**
- Financial records
- Legal documents
- Regulatory compliance (HIPAA, SOX)
- Blockchain-style data integrity

### Implementation Approaches

#### A. Object Lock (MinIO Enterprise Feature)
```python
# Set retention policy on bucket
self.client.set_object_lock_config(
    bucket_name=self.bucket_name,
    config=ObjectLockConfig(
        mode=COMPLIANCE,  # or GOVERNANCE
        retention_days=365
    )
)
```

**Modes:**
- **COMPLIANCE:** Cannot be deleted by anyone (not even root)
- **GOVERNANCE:** Can be deleted with special permissions

#### B. Application-Level Checks
```python
def upload_immutable(self, file_path: str, object_name: str):
    # Check if object already exists
    if self._object_exists(object_name):
        raise ImmutableStorageError(
            f"Object '{object_name}' already exists and cannot be overwritten"
        )
    return self.upload_file(file_path, object_name)
```

**Pros:** Works with any storage system
**Cons:** Requires discipline, can be bypassed

---

## 3. Timestamp-Based Naming Convention

**Use Case:** When you want version control through naming without enabling versioning

**Examples:**
- Daily reports: `sales-report-2024-01-15.pdf`
- Log files: `app-log-2024-01-15-14-30-00.log`
- Data snapshots: `user-data-snapshot-1704067200.json`

### Implementation Approaches

#### A. Human-Readable Timestamps
```python
from datetime import datetime

def upload_with_timestamp(self, file_path: str, base_name: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name, ext = os.path.splitext(base_name)
    object_name = f"{name}_{timestamp}{ext}"
    return self.upload_file(file_path, object_name)

# Example: "report.pdf" → "report_2024-10-04_14-30-15.pdf"
```

#### B. Unix Timestamp (Epoch)
```python
import time

def upload_with_epoch(self, file_path: str, base_name: str):
    epoch = int(time.time())
    name, ext = os.path.splitext(base_name)
    object_name = f"{name}_{epoch}{ext}"
    return self.upload_file(file_path, object_name)

# Example: "report.pdf" → "report_1696428615.pdf"
```

**Pros:** Simple, no special features needed, easy to query by date
**Cons:** Filename length increases, need to parse names to find versions

#### C. Organized by Date Hierarchy
```python
def upload_dated_path(self, file_path: str, base_name: str):
    now = datetime.now()
    object_name = f"{now.year}/{now.month:02d}/{now.day:02d}/{base_name}"
    return self.upload_file(file_path, object_name)

# Example: "report.pdf" → "2024/10/04/report.pdf"
```

**Pros:** Natural organization, easy to list by date range
**Cons:** Same filename on same day overwrites

---

## 4. Comparison Table

| Strategy | Storage Cost | Complexity | Query Performance | Compliance-Ready |
|----------|--------------|------------|-------------------|------------------|
| **Built-in Versioning** | High (keeps all) | Low | Medium | Yes |
| **Immutable Lock** | Medium | Low | High | Yes |
| **Timestamp Names** | Medium | Medium | High | Partial |
| **App-Level Versioning** | Medium | High | Medium | Partial |

---

## 5. Best Practices

### When to Use Each Strategy

**Use Versioning when:**
- You need complete audit trails
- Users might need to recover old versions
- Compliance requires version history

**Use Immutability when:**
- Data must never change (legal/financial)
- Regulatory compliance (WORM requirements)
- Security is paramount

**Use Timestamp Naming when:**
- You want simple, predictable naming
- You're generating time-series data
- You need human-readable organization

### Combining Strategies

You can combine approaches:
```python
# Timestamped names + versioning enabled
# Provides both human readability AND version history
object_name = f"reports/{timestamp}/quarterly-report.pdf"
```

---

## 6. Implementation Roadmap

**Phase 1: Current** ✅
- Basic CRUD operations
- Single bucket management

**Phase 2: Naming Conventions** 
- Implement timestamp-based naming
- Add hierarchical path organization
- Search/filter by date ranges

**Phase 3: Versioning**
- Enable MinIO versioning
- Add version listing functionality
- Implement version retrieval

**Phase 4: Immutability**
- Add immutability checks
- Implement retention policies
- Add compliance reporting

---

## 7. Code Examples to Implement Later

Save these for future reference:

```python
class AdvancedObjectStorage(ObjectStorageClient):
    """Extended client with versioning support"""
    
    def list_versions(self, object_name: str):
        """List all versions of an object"""
        versions = self.client.list_objects(
            self.bucket_name,
            prefix=object_name,
            include_version=True
        )
        return [(v.object_name, v.version_id) for v in versions]
    
    def download_version(self, object_name: str, version_id: str, save_path: str):
        """Download a specific version"""
        self.client.fget_object(
            self.bucket_name,
            object_name,
            save_path,
            version_id=version_id
        )
    
    def make_immutable(self, object_name: str, days: int):
        """Set retention period on object"""
        from datetime import datetime, timedelta
        retention_date = datetime.utcnow() + timedelta(days=days)
        
        self.client.set_object_retention(
            self.bucket_name,
            object_name,
            config=Retention(
                mode=COMPLIANCE,
                retain_until_date=retention_date
            )
        )
```

---

## 8. Further Reading

- [MinIO Versioning Documentation](https://min.io/docs/minio/linux/administration/object-management/object-versioning.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [WORM Storage Best Practices](https://en.wikipedia.org/wiki/Write_once_read_many)

---

**Note:** These are advanced features. Master the basics first, then return to implement these as needed for your specific use cases.