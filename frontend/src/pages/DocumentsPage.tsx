import { useState, useEffect } from 'react';
import { FileText, Download, CheckCircle, XCircle, AlertCircle, Clock, Upload, X } from 'lucide-react';
import { documentsAPI } from '@/services/api';
import type { User, Document, DocumentStatus, ApprovalChainType, DocumentUploadPayload } from '@/types';
import { ApprovalAction } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';

interface DocumentsPageProps {
  user: User;
}

export default function DocumentsPage({ user }: DocumentsPageProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | DocumentStatus>('all');
  const [error, setError] = useState<string>('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [approvalComments, setApprovalComments] = useState('');
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [approvalAction, setApprovalAction] = useState<ApprovalAction | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsAPI.getDocuments();
      setDocuments(data);
      setError('');
    } catch (err: any) {
      console.error('Error loading documents:', err);
      setError(err.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const file = formData.get('file') as File;
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    const payload: DocumentUploadPayload = {
      title: formData.get('title') as string,
      description: formData.get('description') as string || undefined,
      document_type: formData.get('document_type') as string,
      department: formData.get('department') as string,
      approval_chain_type: formData.get('approval_chain_type') as ApprovalChainType,
      file,
    }

    try {
      setUploading(true);
      await documentsAPI.createDocument(payload);
      setShowUploadModal(false);
      loadDocuments();
      setError('');
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleApproval = async () => {
    if (!selectedDoc || !approvalAction) return;

    try {
      await documentsAPI.approveDocument(selectedDoc.id, approvalAction, approvalComments || undefined);
      setShowApprovalDialog(false);
      setSelectedDoc(null);
      setApprovalComments('');
      setApprovalAction(null);
      loadDocuments();
    } catch (err: any) {
      console.error('Approval error:', err);
      setError(err.response?.data?.detail || 'Failed to process approval');
    }
  };

  const handleDownload = async (docId: number) => {
    try {
      const blob = await documentsAPI.downloadDocument(docId);
      const blobUrl = URL.createObjectURL(blob);
      window.open(blobUrl);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const openApprovalDialog = (doc: Document, action: ApprovalAction) => {
    setSelectedDoc(doc);
    setApprovalAction(action);
    setShowApprovalDialog(true);
  };

  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'revision_requested':
        return <AlertCircle className="w-5 h-5 text-orange-600" />;
      default:
        return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: DocumentStatus) => {
    const styles = {
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      revision_requested: 'bg-orange-100 text-orange-800',
      draft: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const filteredDocuments = filter === 'all' 
    ? documents 
    : documents.filter(doc => doc.status === filter);

  const pendingApprovals = documents.filter(
    doc => doc.status === 'pending' && doc.current_approver_id === user.id
  );

  if (loading) {
    return <LoadingSpinner text="Loading documents..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Manage documents and approvals</p>
        </div>
        <button 
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Upload className="w-4 h-4" />
          Upload Document
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {pendingApprovals.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-yellow-900">
              You have {pendingApprovals.length} document{pendingApprovals.length > 1 ? 's' : ''} pending your approval
            </span>
          </div>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          All ({documents.length})
        </button>
        <button
          onClick={() => setFilter('pending' as DocumentStatus)}
          className={`px-4 py-2 rounded-lg ${
            filter === 'pending'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Pending ({documents.filter(d => d.status === 'pending').length})
        </button>
        <button
          onClick={() => setFilter('approved' as DocumentStatus)}
          className={`px-4 py-2 rounded-lg ${
            filter === 'approved'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Approved ({documents.filter(d => d.status === 'approved').length})
        </button>
        <button
          onClick={() => setFilter('revision_requested' as DocumentStatus)}
          className={`px-4 py-2 rounded-lg ${
            filter === 'revision_requested'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Revision Requested ({documents.filter(d => d.status === 'revision_requested').length})
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No documents found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(doc.status)}
                        <div>
                          <div className="font-medium text-gray-900">{doc.title}</div>
                          {doc.description && (
                            <div className="text-sm text-gray-500">{doc.description}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {doc.document_type}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {doc.department}
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(doc.status)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {doc.status === 'pending' && doc.current_approver_id === user.id && (
                          <>
                            <button 
                              onClick={() => openApprovalDialog(doc, ApprovalAction.APPROVED)}
                              className="text-green-600 hover:text-green-800 text-sm font-medium"
                            >
                              Approve
                            </button>
                            <button 
                              onClick={() => openApprovalDialog(doc, ApprovalAction.REJECTED)}
                              className="text-red-600 hover:text-red-800 text-sm font-medium"
                            >
                              Reject
                            </button>
                            <button 
                              onClick={() => openApprovalDialog(doc, ApprovalAction.REVISION_REQUESTED)}
                              className="text-orange-600 hover:text-orange-800 text-sm font-medium"
                            >
                              Request Revision
                            </button>
                          </>
                        )}
                        <button 
                          onClick={() => handleDownload(doc.id)}
                          className="text-gray-600 hover:text-gray-800"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Upload Document</h2>
              <button onClick={() => setShowUploadModal(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  name="title"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  name="description"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Type *</label>
                <select
                  name="document_type"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select type</option>
                  <option value="Budget">Budget</option>
                  <option value="Academic">Academic</option>
                  <option value="Report">Report</option>
                  <option value="Purchase">Purchase</option>
                  <option value="Policy">Policy</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                <select
                  name="department"
                  required
                  defaultValue={user.department}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Computer Science">Computer Science</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Mechanical">Mechanical</option>
                  <option value="Civil">Civil</option>
                  <option value="Administration">Administration</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Approval Chain *</label>
                <select
                  name="approval_chain_type"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="routine">Routine (HOD → VP)</option>
                  <option value="financial">Financial (HOD → Principal)</option>
                  <option value="strategic">Strategic (HOD → VP → Principal → Director)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File *</label>
                <input
                  type="file"
                  name="file"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Approval Dialog */}
      {showApprovalDialog && selectedDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {approvalAction === ApprovalAction.APPROVED && 'Approve Document'}
                {approvalAction === ApprovalAction.REJECTED && 'Reject Document'}
                {approvalAction === ApprovalAction.REVISION_REQUESTED && 'Request Revision'}
              </h2>
              <button onClick={() => setShowApprovalDialog(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mb-4">
              <p className="text-sm text-gray-600">Document: <span className="font-medium">{selectedDoc.title}</span></p>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Comments</label>
              <textarea
                value={approvalComments}
                onChange={(e) => setApprovalComments(e.target.value)}
                rows={4}
                placeholder="Add your comments (optional)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowApprovalDialog(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleApproval}
                className={`px-4 py-2 text-white rounded-lg ${
                  approvalAction === ApprovalAction.APPROVED ? 'bg-green-600 hover:bg-green-700' :
                  approvalAction === ApprovalAction.REJECTED ? 'bg-red-600 hover:bg-red-700' :
                  'bg-orange-600 hover:bg-orange-700'
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
